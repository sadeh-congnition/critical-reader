from django.contrib import admin


from .models import (
    ResourceRow,
    ConversationRow,
)


@admin.register(ResourceRow)
class ResourceTableAdmin(admin.ModelAdmin):
    list_display = ("status", "url", "date_created", "date_updated")


@admin.register(ConversationRow)
class ConversationTableAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "date_created",
        "date_updated",
    )
