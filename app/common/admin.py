from django.contrib import admin


from .models import (
    ResourceRow,
    ProjectRow,
    ReadingPalChat,
)


@admin.register(ReadingPalChat)
class ChatTableAdmin(admin.ModelAdmin):
    list_display = ("name", "id_for_ui", "date_added", "date_updated")


@admin.register(ResourceRow)
class ResourceTableAdmin(admin.ModelAdmin):
    list_display = ("status", "url", "date_created", "date_updated")


@admin.register(ProjectRow)
class ProjectTableAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date_created",
        "date_updated",
    )
