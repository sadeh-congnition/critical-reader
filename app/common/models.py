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
    config = models.JSONField(default=dict)

    @classmethod
    def create(cls, configs: ConversationConfig):
        cls.objects.create(config=configs.to_dict())

    @classmethod
    async def all(cls):
        res = []
        async for r in cls.objects.all():
            res.append(r)
        return res


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


async def get_conversations() -> list[Conversation]:
    res = []
    conversation_rows = await ConversationTable.all()
    for c in conversation_rows:
        for r in c.resources.all():
            res.append(
                Conversation(
                    id_in_db=c.id,
                    id_for_ui=f"converstaion-{c.id}",
                    resources=[Resource(name=r.name, status=r.status)],
                    status=c.status,
                )
            )
    return res
