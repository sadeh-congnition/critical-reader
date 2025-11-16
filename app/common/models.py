from typing import Self
from dataclasses import dataclass

from django.db import models


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
        NEW = "NEW"
        PROCESSING_RESOURCES = "Processing resources"

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=1024, choices=Status.choices, default=Status.NEW
    )

    def __str__(self):
        return f"conversation-{self.id}: {str(self.status)}"

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
            resources.append(Resource(url=r.url, status=r.status))

        config_row = await ConversationConfigRow.aget_by_conversation(self.id)
        if config_row:
            config = await config_row.ato_dict()
        else:
            config = {}
        return Conversation(
            id_in_db=self.id,
            id_for_ui=f"conversation-{self.id}",
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
        NEW = "New"
        DOWNLOAD_IN_PROGRESS = "Download in progress"

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

    @classmethod
    async def aget_all_by_conversation_id_for_ui(cls, conversation_id_for_ui: str):
        res = []
        async for r in cls.objects.filter(
            conversation_id=int(conversation_id_for_ui.split("conversation-")[-1])
        ):
            res.append(r)
        return res

    @classmethod
    async def acreate(cls, conversation_id_for_ui: str, url: str):
        await cls.objects.acreate(
            conversation_id=int(conversation_id_for_ui.split("conversation-")[-1]),
            url=url,
        )


class DownloaderRow(models.Model):
    class Downloader(models.TextChoices):
        WEB_SCRAPER = "Web page scraper"

    downloader = models.CharField(
        max_length=1024, choices=Downloader.choices, unique=True
    )

    @classmethod
    async def aget_by_id(cls, id) -> Self:
        res = await cls.objects.aget(id=id)
        return res

    def __str__(self):
        return self.downloader

    def to_dict(self) -> dict:
        return {"name": self.downloader}

    @classmethod
    def create_default_rows(cls):
        cls.objects.get_or_create(downloader=cls.Downloader.WEB_SCRAPER)


class TextExtractorRow(models.Model):
    class Provider(models.TextChoices):
        JINA_API = "jina"
        LOCAL = "ollama"

    class ModelName(models.TextChoices):
        READER_LM_V2 = "ReaderLM-v2"

    provider = models.CharField(max_length=1024, choices=Provider.choices)
    model_name = models.CharField(max_length=1024, choices=ModelName.choices)

    @classmethod
    async def aget(cls, id) -> Self:
        res = await cls.objects.aget(id=id)
        return res

    class Meta:
        unique_together = [("provider", "model_name")]

    def __str__(self):
        return self.model_name

    def to_dict(self) -> dict:
        return {"provider": self.provider, "model_name": self.model_name}

    @classmethod
    def create_default_rows(cls):
        cls.objects.get_or_create(
            provider=cls.Provider.JINA_API, model_name=cls.ModelName.READER_LM_V2
        )


class EmbedderRow(models.Model):
    class Provider(models.TextChoices):
        LOCAL = "ollama"
        JINA_API = "jina"

    class ModelName(models.TextChoices):
        JINA_EMBEDDINGS_V4 = "jina-embeddings-v4"

    provider = models.CharField(max_length=1024, choices=Provider.choices)
    model_name = models.CharField(max_length=1024, choices=ModelName.choices)

    @classmethod
    async def aget(cls, id) -> Self:
        res = await cls.objects.aget(id=id)
        return res

    class Meta:
        unique_together = [("provider", "model_name")]

    def __str__(self):
        return f"{self.provider}-{self.model_name}"

    def to_dict(self) -> dict:
        return {"provider": self.provider, "model_name": self.model_name}

    @classmethod
    def create_default_rows(cls):
        cls.objects.get_or_create(
            provider=cls.Provider.JINA_API, model_name=cls.ModelName.JINA_EMBEDDINGS_V4
        )


class ChunkerRow(models.Model):
    class Type(models.TextChoices):
        FIXED = "Fixed size"
        NO_CHUNK = "No chunking"

    type = models.CharField(max_length=1024, choices=Type.choices)
    size = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("type", "size")]

    @classmethod
    async def aget_by_id(cls, id) -> Self:
        res = await cls.objects.aget(id=id)
        return res

    def to_dict(self) -> dict:
        return {"type": self.type, "size": self.size}

    def __str__(self):
        return f"{self.type}, {self.size}"

    @classmethod
    def create_default_rows(cls):
        cls.objects.get_or_create(type=cls.Type.FIXED, size=1024)
        cls.objects.get_or_create(type=cls.Type.NO_CHUNK)

    @classmethod
    def default(cls) -> Self:
        return cls.objects.get(type=cls.Type.FIXED, size=1024)

    @classmethod
    def no_chunk(cls) -> Self:
        return cls.objects.get(type=cls.Type.NO_CHUNK)


class ProcessorRow(models.Model):
    class Type(models.TextChoices):
        SIMPLE_RAG = "Simple RAG"

    type = models.CharField(max_length=1024, choices=Type.choices)
    chunker = models.ForeignKey(ChunkerRow, on_delete=models.CASCADE)

    class Meta:
        unique_together = [("type", "chunker")]

    @classmethod
    async def aget(cls, id) -> Self:
        res = await cls.objects.aget(id=id)
        return res

    @classmethod
    def create_default_rows(cls):
        cls.objects.get_or_create(
            type=cls.Type.SIMPLE_RAG,
            chunker=ChunkerRow.default(),
        )
        cls.objects.get_or_create(
            type=cls.Type.SIMPLE_RAG,
            chunker=ChunkerRow.no_chunk(),
        )

    def to_dict(self) -> dict:
        return {"type": self.type, "chunker": self.chunker.to_dict()}

    async def ato_dict(self) -> dict:
        chunker = await ChunkerRow.aget_by_id(self.chunker_id)
        return {"type": self.type, "chunker": chunker.to_dict()}

    def __str__(self):
        return f"{self.type}, {self.chunker}"


class ConversationConfigRow(models.Model):
    conversation = models.OneToOneField(ConversationRow, on_delete=models.CASCADE)
    downloader = models.ForeignKey(DownloaderRow, on_delete=models.CASCADE)
    text_extractor = models.ForeignKey(TextExtractorRow, on_delete=models.CASCADE)
    embedder = models.ForeignKey(EmbedderRow, on_delete=models.CASCADE)
    processor = models.ForeignKey(ProcessorRow, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.downloader}, {self.text_extractor}, {self.embedder}"

    def to_dict(self) -> dict:
        return {
            "downloader": self.downloader.to_dict(),
            "text_extractor": self.text_extractor.to_dict(),
            "embedder": self.embedder.to_dict(),
            "processor": self.processor.to_dict(),
        }

    async def ato_dict(self) -> dict:
        downloader = await DownloaderRow.aget_by_id(self.downloader_id)
        text_extractor = await TextExtractorRow.aget(self.text_extractor_id)
        embedder = await EmbedderRow.aget(self.embedder_id)
        processor = await ProcessorRow.aget(self.processor_id)
        return {
            "downloader": downloader.to_dict(),
            "text_extractor": text_extractor.to_dict(),
            "embedder": embedder.to_dict(),
            "processor": await processor.ato_dict(),
        }

    @classmethod
    async def aget_by_conversation(cls, conversation_id: int | str) -> Self | None:
        try:
            res = await cls.objects.aget(conversation_id=conversation_id)
            return res
        except cls.DoesNotExist:
            return


def create_default_rows():
    DownloaderRow.create_default_rows()
    TextExtractorRow.create_default_rows()
    EmbedderRow.create_default_rows()
    ChunkerRow.create_default_rows()
    ProcessorRow.create_default_rows()
