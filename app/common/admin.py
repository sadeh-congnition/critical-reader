from django.contrib import admin


from .models import ResourceTable, ConversationTable


@admin.register(ResourceTable)
class ResourceTableAdmin(admin.ModelAdmin):
    pass


@admin.register(ConversationTable)
class ConversationTableAdmin(admin.ModelAdmin):
    pass
