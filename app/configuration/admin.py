from django.contrib import admin
from .models import (
    LLMModelRow,
    ProjectConfigRow,
    DownloaderRow,
    TextExtractorRow,
    EmbedderRow,
    ProcessorRow,
    ChunkerRow,
)


@admin.register(LLMModelRow)
class LLMModelTableAdmin(admin.ModelAdmin):
    list_display = ("model_name",)


@admin.register(ProcessorRow)
class ProcessorTableAdmin(admin.ModelAdmin):
    list_display = ("type", "chunker")


@admin.register(ChunkerRow)
class ChunkerTableAdmin(admin.ModelAdmin):
    list_display = ("type", "size")


@admin.register(DownloaderRow)
class DownloaderTableAdmin(admin.ModelAdmin):
    list_display = ("downloader",)


@admin.register(TextExtractorRow)
class JinaAIExtractorTableAdmin(admin.ModelAdmin):
    list_display = (
        "provider",
        "model_name",
    )


@admin.register(ProjectConfigRow)
class ProjectConfigTableAdmin(admin.ModelAdmin):
    list_display = ("project", "downloader", "text_extractor")


@admin.register(EmbedderRow)
class EmbedderTableAdmin(admin.ModelAdmin):
    list_display = ("provider", "model_name")
