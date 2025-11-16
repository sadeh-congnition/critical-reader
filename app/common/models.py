from enum import Enum
from asgiref.sync import sync_to_async, async_to_sync
from dataclasses import dataclass

from django.db import models


class ResourceTable(models.Model):
    class Status(models.TextChoices):
        NEW = "New"
        DOWNLOAD_IN_PROGRESS = "Download in progress"

    name = models.CharField(max_length=1024)
    url = models.URLField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)


class Downloader(str, Enum):
    WEB_SCRAPER = "Web page scraper"


@dataclass
class ConversationConfig:
    downloader: Downloader

    def to_dict(self):
        return {"downloader": self.downloader.value}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(downloader=Downloader(data["downloader"]))


@dataclass
class Resource:
    name: str
    status: str


@dataclass
class Conversation:
    id_in_db: int | str
    id_for_ui: str
    resources: list[Resource]
    status: str

    def __str__(self):
        return f"{self.id_for_ui}: {str(self.status)}"


class ConversationTable(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW"
        PROCESSING_RESOURCES = "Processing resources"

    resources = models.ManyToManyField(ResourceTable)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=1024, choices=Status.choices, default=Status.NEW
    )
    config = models.JSONField(default=dict, blank=True, null=True)

    @classmethod
    async def acreate(cls):
        res = await cls.objects.acreate()
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
        resources = []
        async for r in self.resources.all():
            resources.append(Resource(name=r.name, status=r.status))
        return Conversation(
            id_in_db=self.id,
            id_for_ui=f"converstaion-{self.id}",
            resources=resources,
            status=self.status,
        )


def get_conversations() -> list[Conversation]:
    res = []
    conversation_rows = ConversationTable.all()
    for c in conversation_rows:
        res.append(c.conversation())
    return res


async def aget_conversations() -> list[Conversation]:
    res = []
    conversation_rows = await ConversationTable.aall()
    for c in conversation_rows:
        convo = await c.conversation()
        res.append(convo)
    return res
