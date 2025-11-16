from django.contrib import admin


from .models import (
    ResourceRow,
    ConversationRow,
    ConversationConfigRow,
    DownloaderRow,
    TextExtractorRow,
    EmbedderRow,
    ProcessorRow,
    ChunkerRow,
)


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
    list_display = ("model_name",)


@admin.register(ConversationConfigRow)
class ConversationConfigTableAdmin(admin.ModelAdmin):
    list_display = ("conversation", "downloader", "text_extractor")


@admin.register(EmbedderRow)
class EmbedderTableAdmin(admin.ModelAdmin):
    list_display = ("provider", "model_name")


@admin.register(ResourceRow)
class ResourceTableAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "url", "date_created", "date_updated")


@admin.register(ConversationRow)
class ConversationTableAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "date_created",
        "date_updated",
        "conversationconfigrow",
    )
