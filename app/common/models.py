from dataclasses import dataclass
from datetime import datetime
from typing import Self

from django.db import models

from common.constants import (
    ConversationStatus,
    ResourceStatus,
    EventTypes,
)


@dataclass
class Resource:
    url: str
    status: str


@dataclass
class Conversation:
    id_in_db: int | str
    id_for_ui: str
    resources: list[Resource]
    status: str
    config: dict

    def __str__(self):
        return f"{self.id_for_ui}: {str(self.status)}"


class ConversationRow(models.Model):
    class Status(models.TextChoices):
        NEW = ConversationStatus.NEW, ConversationStatus.NEW
        PROCESSING_RESOURCES = (
            ConversationStatus.PROCESSING_RESOURCES,
            ConversationStatus.PROCESSING_RESOURCES,
        )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=1024, choices=Status.choices, default=Status.NEW
    )

    @classmethod
    async def aget_by_id(cls, row_id) -> Self | None:
        try:
            res = await cls.objects.aget(id=row_id)
            return res
        except cls.DoesNotExist:
            return

    @property
    def id_for_ui(self):
        return f"conversation-{self.id}"

    @classmethod
    def db_id_from_ui_id(cls, ui_id) -> int:
        return int(ui_id.split("conversation-")[-1])

    def __str__(self):
        return f"conversation-{self.id}: {str(self.status)}"

    @classmethod
    async def acreate(cls):
        res = await cls.objects.acreate()
        await EventLogRows.acreate(res.id, EventTypes.CONVERSATION_CREATED, res.id)
        return res

    @classmethod
    async def aall(cls):
        res = []
        async for r in cls.objects.all():
            res.append(r)
        return res

    @classmethod
    def all(cls):
        return cls.objects.all()

    async def conversation(self) -> Conversation:
        from configuration.models import ConversationConfigRow

        resources = []
        async for r in self.resources.order_by("-date_updated").all():
            resources.append(Resource(url=r.url, status=r.status))

        config_row = await ConversationConfigRow.aget_by_conversation(self.id)
        if config_row:
            config = await config_row.ato_dict()
        else:
            config = {}
        return Conversation(
            id_in_db=self.id,
            id_for_ui=self.id_for_ui,
            resources=resources,
            status=self.status,
            config=config,
        )

    @classmethod
    def get_conversations(cls) -> list[Conversation]:
        res = []
        conversation_rows = ConversationRow.all()
        for c in conversation_rows:
            res.append(c.conversation())
        return res

    @classmethod
    async def aget_conversations(cls) -> list[Conversation]:
        res = []
        conversation_rows = await ConversationRow.aall()
        for c in conversation_rows:
            convo = await c.conversation()
            res.append(convo)
        return res


class ResourceRow(models.Model):
    class Status(models.TextChoices):
        NEW = ResourceStatus.NEW, ResourceStatus.NEW
        DOWNLOADED = ResourceStatus.DOWNLOADED, ResourceStatus.DOWNLOADED
        SCRAPED = ResourceStatus.SCRAPED, ResourceStatus.SCRAPED
        ERROR = ResourceStatus.ERROR, ResourceStatus.ERROR
        PROCESSED = ResourceStatus.PROCESSED, ResourceStatus.PROCESSED

    conversation = models.ForeignKey(
        ConversationRow, on_delete=models.CASCADE, related_name="resources"
    )
    url = models.URLField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=1024, choices=Status.choices, default=Status.NEW
    )
    scraped_content = models.TextField(null=True, blank=True)
    error_msg = models.TextField(null=True, blank=True)

    def set_download_finishied(self):
        self.status = self.Status.DOWNLOADED
        self.save()

    def set_scraping_finished(self):
        self.status = self.Status.SCRAPED
        self.save()

    def set_processed(self):
        self.status = self.Status.PROCESSED
        self.save()

    def add_error(self, error_msg: str):
        self.status = self.Status.ERROR
        self.error_msg = error_msg
        self.save()

    async def aadd_error(self, error_msg: str):
        self.status = self.Status.ERROR
        self.error_msg = error_msg
        await self.asave()

    @classmethod
    async def aget_all_by_conversation_id_for_ui(cls, conversation_id_for_ui: str):
        res = []
        async for r in cls.objects.filter(
            conversation_id=ConversationRow.db_id_from_ui_id(conversation_id_for_ui)
        ).order_by("-date_updated"):
            res.append(r)
        return res

    @classmethod
    async def acreate(cls, conversation_id_for_ui: str, url: str):
        res = await cls.objects.acreate(
            conversation_id=ConversationRow.db_id_from_ui_id(conversation_id_for_ui),
            url=url,
        )
        await EventLogRows.acreate(
            ConversationRow.db_id_from_ui_id(conversation_id_for_ui),
            EventTypes.RESOURCE_ADDED,
            res.id,
        )
        return res

    @classmethod
    def get_by_id(cls, id: int | str) -> Self | None:
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            return

    def add_scraped_content(self, content: str):
        self.scraped_content = content
        self.save()


@dataclass
class EventLog:
    conversation_db_id: int
    event_type: str
    date_created: datetime
    entity_id: str

    def human_readable(self) -> str:
        return f"|{self.date_created}| {self.event_type}: {self.entity_id}"


class EventLogRows(models.Model):
    class EventType(models.TextChoices):
        CONVERSATION_CREATED = (
            EventTypes.CONVERSATION_CREATED,
            EventTypes.CONVERSATION_CREATED,
        )
        RESOURCE_ADDED = EventTypes.RESOURCE_ADDED, EventTypes.RESOURCE_ADDED

    type = models.CharField(max_length=1024, choices=EventType.choices)
    conversation = models.ForeignKey(ConversationRow, on_delete=models.CASCADE)
    entity_id = models.CharField(max_length=1024)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, conversation_id: int, type, entity_id):
        res = cls.objects.create(
            type=type, conversation_id=conversation_id, entity_id=entity_id
        )
        return res

    @classmethod
    async def acreate(cls, conversation_id: int, type, entity_id):
        res = await cls.objects.acreate(
            type=type, conversation_id=conversation_id, entity_id=entity_id
        )
        return res

    @classmethod
    async def aget_logs_for_conversation(cls, conversation_id_for_ui) -> list[EventLog]:
        conv_row = await ConversationRow.aget_by_id(
            ConversationRow.db_id_from_ui_id(conversation_id_for_ui)
        )
        if not conv_row:
            raise ValueError(f"Unknown conversation: {conversation_id_for_ui}")

        logs = []
        async for l in cls.objects.filter(conversation=conv_row).order_by(
            "date_updated"
        ):
            logs.append(
                EventLog(
                    conversation_db_id=conv_row.id,
                    event_type=l.type,
                    date_created=l.date_created,
                    entity_id=l.entity_id,
                )
            )

        return logs
