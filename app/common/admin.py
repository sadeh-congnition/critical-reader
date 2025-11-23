from django.contrib import admin


from .models import (
    ResourceRow,
    ProjectRow,
)


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
