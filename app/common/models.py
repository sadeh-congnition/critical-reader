from dataclasses import dataclass
from typing import TYPE_CHECKING
from datetime import datetime
from typing import Self

from django.db import models

from common.constants import (
    ResourceStatus,
    EventTypes,
)

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


@dataclass
class Resource:
    url: str
    status: str


class ResourceRow(models.Model):
    class Status(models.TextChoices):
        NEW = ResourceStatus.NEW, ResourceStatus.NEW
        DOWNLOADED = ResourceStatus.DOWNLOADED, ResourceStatus.DOWNLOADED
        SCRAPED = ResourceStatus.SCRAPED, ResourceStatus.SCRAPED
        ERROR = ResourceStatus.ERROR, ResourceStatus.ERROR
        PROCESSED = ResourceStatus.PROCESSED, ResourceStatus.PROCESSED

    project = models.ForeignKey(
        "ProjectRow", on_delete=models.CASCADE, related_name="resources"
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
    if TYPE_CHECKING:
        id: int

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
    async def aget_all_by_project_id(cls, project_id: int):
        async for r in cls.objects.filter(
            project_id=project_id,
        ).order_by("-date_updated"):
            yield r

    @classmethod
    async def acreate(cls, project_id: int, url: str):
        res = await cls.objects.acreate(
            project_id=project_id,
            url=url,
        )
        await EventLogRows.acreate(
            project_id,
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


class ProjectRow(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    if TYPE_CHECKING:
        id: int
        resources: RelatedManager[ResourceRow]

    @classmethod
    async def get_by_id(cls, row_id: int) -> Self | None:
        try:
            res = cls.objects.get(id=row_id)
            return res
        except cls.DoesNotExist:
            return

    @classmethod
    async def aget_by_id(cls, row_id: int) -> Self | None:
        try:
            res = await cls.objects.aget(id=row_id)
            return res
        except cls.DoesNotExist:
            return

    def __str__(self):
        return f"project-{self.id}"

    @classmethod
    async def acreate(cls):
        res = await cls.objects.acreate()
        await EventLogRows.acreate(res.id, EventTypes.PROJECT_CREATED, res.id)
        return res

    @classmethod
    async def aall(cls):
        async for r in cls.objects.all():
            yield r

    @classmethod
    def all(cls):
        return cls.objects.all()


@dataclass
class EventLog:
    project_db_id: int
    event_type: str
    date_created: datetime
    entity_id: str

    def human_readable(self) -> str:
        return f"|{self.date_created}| {self.event_type}: {self.entity_id}"


class EventLogRows(models.Model):
    class EventType(models.TextChoices):
        PROJECT_CREATED = EventTypes.PROJECT_CREATED, EventTypes.PROJECT_CREATED
        RESOURCE_ADDED = EventTypes.RESOURCE_ADDED, EventTypes.RESOURCE_ADDED
        CHAT_CREATED = EventTypes.CHAT_CREATED, EventTypes.CHAT_CREATED

    type = models.CharField(max_length=1024, choices=EventType.choices)
    project = models.ForeignKey(ProjectRow, on_delete=models.CASCADE)
    entity_id = models.CharField(max_length=1024)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, project_id: int, type, entity_id):
        res = cls.objects.create(type=type, project_id=project_id, entity_id=entity_id)
        return res

    @classmethod
    async def acreate(cls, project_id: int, type, entity_id):
        res = await cls.objects.acreate(
            type=type, project_id=project_id, entity_id=entity_id
        )
        return res

    @classmethod
    async def aget_logs_for_project(cls, project_id: int) -> list[EventLog]:
        project_row = await ProjectRow.aget_by_id(project_id)
        if not project_row:
            raise ValueError(f"Unknown project: {project_id}")

        logs = []
        async for l in cls.objects.filter(project=project_row).order_by("date_updated"):
            logs.append(
                EventLog(
                    project_db_id=project_row.id,
                    event_type=l.type,
                    date_created=l.date_created,
                    entity_id=l.entity_id,
                )
            )

        return logs


class ReadingPalChat(models.Model):
    project = models.ForeignKey(ProjectRow, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    id: int

    @classmethod
    async def aget_all(cls, project_id):
        async for r in cls.objects.filter(project_id=project_id).order_by(
            "-date_updated"
        ):
            yield r

    @classmethod
    async def acreate(cls, project_id):
        return await cls.objects.acreate(project_id=project_id, name="New chat")
