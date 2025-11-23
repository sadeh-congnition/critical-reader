from dataclasses import dataclass
from typing import Self

from django.db import models
from common.models import ProjectRow
from common.constants import (
    DownloaderType,
    JINA_AI_MODELS,
    Provider,
    ChunkerType,
    ProcessorType,
)


@dataclass
class Downloader:
    type: str

    def validate(self):
        assert self.type in [DownloaderType.JINA_AI_READER_USING_JINA_API]


class DownloaderRow(models.Model):
    class Downloader(models.TextChoices):
        WEB_SCRAPER = DownloaderType.WEB_PAGE_SCRAPER, DownloaderType.WEB_PAGE_SCRAPER
        JINA_AI_API = (
            DownloaderType.JINA_AI_READER_USING_JINA_API,
            DownloaderType.JINA_AI_READER_USING_JINA_API,
        )

    downloader = models.CharField(
        max_length=1024, choices=Downloader.choices, unique=True
    )

    @classmethod
    def get_by_id(cls, id) -> Self:
        res = cls.objects.get(id=id)
        return res

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
        cls.objects.get_or_create(downloader=cls.Downloader.JINA_AI_API)

    def to_obj(self) -> Downloader:
        return Downloader(type=self.downloader)


@dataclass
class TextExtractor:
    provider: str
    model_name: str
    downloader: Downloader

    def validate(self):
        if self.downloader.type == DownloaderType.JINA_AI_READER_USING_JINA_API:
            assert self.provider == TextExtractorRow.Provider.JINA_API
            assert self.model_name in JINA_AI_MODELS.reader_models()


class TextExtractorRow(models.Model):
    class Provider(models.TextChoices):
        JINA_API = Provider.JINA, Provider.JINA
        LOCAL = Provider.OLLAMA, Provider.OLLAMA

    class ModelName(models.TextChoices):
        READER_LM_V2 = JINA_AI_MODELS.READER_LM_V2, JINA_AI_MODELS.READER_LM_V2

    provider = models.CharField(max_length=1024, choices=Provider.choices)
    model_name = models.CharField(max_length=1024, choices=ModelName.choices)

    @classmethod
    def get(cls, id) -> Self:
        res = cls.objects.get(id=id)
        return res

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

    def to_obj(self, downloader: Downloader) -> TextExtractor:
        return TextExtractor(
            provider=self.provider, model_name=self.model_name, downloader=downloader
        )

    @classmethod
    def create_default_rows(cls):
        cls.objects.get_or_create(
            provider=cls.Provider.JINA_API, model_name=cls.ModelName.READER_LM_V2
        )


@dataclass
class Embedder:
    provider: str
    model_name: str

    def validate(self):
        pass


class EmbedderRow(models.Model):
    class Provider(models.TextChoices):
        LOCAL = Provider.OLLAMA, Provider.OLLAMA
        JINA_API = Provider.JINA, Provider.JINA

    class ModelName(models.TextChoices):
        JINA_EMBEDDINGS_V4 = (
            JINA_AI_MODELS.JINA_EMBEDDINGS_V4,
            JINA_AI_MODELS.JINA_EMBEDDINGS_V4,
        )

    provider = models.CharField(max_length=1024, choices=Provider.choices)
    model_name = models.CharField(max_length=1024, choices=ModelName.choices)

    @classmethod
    def get(cls, id) -> Self:
        res = cls.objects.get(id=id)
        return res

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

    def to_obj(self) -> Embedder:
        return Embedder(provider=self.provider, model_name=self.model_name)


@dataclass
class Chunker:
    type: str
    size: int | None


class ChunkerRow(models.Model):
    class Type(models.TextChoices):
        FIXED = ChunkerType.FIXED, ChunkerType.FIXED
        NO_CHUNK = ChunkerType.NO_CHUNK, ChunkerType.NO_CHUNK

    type = models.CharField(max_length=1024, choices=Type.choices)
    size = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("type", "size")]

    @classmethod
    async def aget_by_id(cls, id) -> Self:
        res = await cls.objects.aget(id=id)
        return res

    @classmethod
    def get_by_id(cls, id) -> Self:
        res = cls.objects.get(id=id)
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

    def to_obj(self) -> Chunker:
        return Chunker(type=self.type, size=self.size)


@dataclass
class Processor:
    type: str
    chunker: Chunker

    def validate(self):
        pass


class ProcessorRow(models.Model):
    class Type(models.TextChoices):
        SIMPLE_RAG = ProcessorType.SIMPLE_RAG, ProcessorType.SIMPLE_RAG

    type = models.CharField(max_length=1024, choices=Type.choices)
    chunker = models.ForeignKey(ChunkerRow, on_delete=models.CASCADE)
    chunker_id: int

    class Meta:
        unique_together = [("type", "chunker")]

    @classmethod
    def get(cls, id) -> Self:
        res = cls.objects.get(id=id)
        return res

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

    async def ato_obj(self) -> Processor:
        chunker = await ChunkerRow.aget_by_id(self.chunker_id)
        return Processor(type=self.type, chunker=chunker.to_obj())

    def to_obj(self) -> Processor:
        chunker = ChunkerRow.get_by_id(self.chunker_id)
        return Processor(type=self.type, chunker=chunker.to_obj())


@dataclass
class LLMModel:
    model_name: str

    def validate(self):
        pass


class LLMModelRow(models.Model):
    model_name = models.CharField(max_length=1024)

    @classmethod
    async def aget(cls, id) -> Self:
        res = await cls.objects.aget(id=id)
        return res

    @classmethod
    def create_default_rows(cls):
        cls.objects.get_or_create(model_name="ollama_chat/qwen3:4b")

    def __str__(self):
        return self.model_name

    def to_dict(self) -> dict:
        return {"model_name": self.model_name}

    def to_obj(self) -> LLMModel:
        return LLMModel(model_name=self.model_name)


class ProjectConfigRow(models.Model):
    project = models.OneToOneField(ProjectRow, on_delete=models.CASCADE)
    downloader = models.ForeignKey(DownloaderRow, on_delete=models.CASCADE)
    text_extractor = models.ForeignKey(TextExtractorRow, on_delete=models.CASCADE)
    embedder = models.ForeignKey(EmbedderRow, on_delete=models.CASCADE)
    processor = models.ForeignKey(ProcessorRow, on_delete=models.CASCADE)
    llm_model = models.ForeignKey(LLMModelRow, on_delete=models.CASCADE)
    downloader_id: int
    text_extractor_id: int
    embedder_id: int
    llm_model_id: int
    processor_id: int
    id: int

    def __str__(self):
        return f"{self.downloader}, {self.text_extractor}, {self.embedder}"

    def to_dict(self) -> dict:
        return {
            "downloader": self.downloader.to_dict(),
            "text_extractor": self.text_extractor.to_dict(),
            "embedder": self.embedder.to_dict(),
            "processor": self.processor.to_dict(),
            "llm_model": self.llm_model.to_dict(),
        }

    async def ato_dict(self) -> dict:
        downloader = await DownloaderRow.aget_by_id(self.downloader_id)
        text_extractor = await TextExtractorRow.aget(self.text_extractor_id)
        embedder = await EmbedderRow.aget(self.embedder_id)
        processor = await ProcessorRow.aget(self.processor_id)
        llm_model = await LLMModelRow.aget(self.llm_model_id)
        return {
            "downloader": downloader.to_dict(),
            "text_extractor": text_extractor.to_dict(),
            "embedder": embedder.to_dict(),
            "processor": await processor.ato_dict(),
            "llm_model": llm_model.to_dict(),
        }

    @classmethod
    async def aget_by_project(cls, project_id: int) -> Self | None:
        try:
            res = await cls.objects.aget(project_id=project_id)
            return res
        except cls.DoesNotExist:
            return

    @classmethod
    def get_by_project_id_for_ui(cls, project_id_for_ui: str) -> Self | None:
        try:
            res = cls.objects.get(project_id=cls.db_id_from_ui_id(project_id_for_ui))
            return res
        except cls.DoesNotExist:
            return

    @classmethod
    async def aget_by_project_id_for_ui(cls, project_id_for_ui: str) -> Self | None:
        try:
            res = await cls.objects.aget(
                project_id=cls.db_id_from_ui_id(project_id_for_ui)
            )
            return res
        except cls.DoesNotExist:
            return

    async def ato_obj(self) -> "Config":
        downloader = await DownloaderRow.aget_by_id(self.downloader_id)
        text_extractor = await TextExtractorRow.aget(self.text_extractor_id)
        embedder = await EmbedderRow.aget(self.embedder_id)
        processor = await ProcessorRow.aget(self.processor_id)
        llm_model = await LLMModelRow.aget(self.llm_model_id)

        processor_obj = await processor.ato_obj()
        downloader_obj = downloader.to_obj()

        conf = Config(
            project_id=self.id,
            downloader=downloader_obj,
            text_extractor=text_extractor.to_obj(downloader_obj),
            embedder=embedder.to_obj(),
            processor=processor_obj,
            llm_model=llm_model.to_obj(),
        )

        conf.validate()
        return conf

    def to_obj(self) -> "Config":
        downloader = DownloaderRow.get_by_id(self.downloader_id)
        text_extractor = TextExtractorRow.get(self.text_extractor_id)
        embedder = EmbedderRow.get(self.embedder_id)
        processor = ProcessorRow.get(self.processor_id)
        llm_model = LLMModelRow.get(self.processor_id)

        processor_obj = processor.to_obj()
        downloader_obj = downloader.to_obj()

        conf = Config(
            project_id == self.id,
            downloader=downloader_obj,
            text_extractor=text_extractor.to_obj(downloader_obj),
            embedder=embedder.to_obj(),
            processor=processor_obj,
            llm_model=llm_model.to_obj(),
        )

        conf.validate()
        return conf

    @classmethod
    def db_id_from_ui_id(cls, ui_id) -> int:
        return int(ui_id.split("project-")[-1])


@dataclass
class Config:
    project_id: int | str
    downloader: Downloader
    text_extractor: TextExtractor
    embedder: Embedder
    processor: Processor
    llm_model: LLMModel

    def validate(self):
        self.downloader.validate()
        self.text_extractor.validate()
        self.embedder.validate()
        self.processor.validate()
        self.llm_model.validate()


def create_default_rows():
    DownloaderRow.create_default_rows()
    TextExtractorRow.create_default_rows()
    EmbedderRow.create_default_rows()
    ChunkerRow.create_default_rows()
    ProcessorRow.create_default_rows()
    LLMModelRow.create_default_rows()
