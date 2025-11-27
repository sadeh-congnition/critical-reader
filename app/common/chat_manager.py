from dataclasses import dataclass
from datetime import datetime

from .models import ReadingPalChat
from configuration.models import ProjectConfigRow
from common.models import EventLogRows


@dataclass
class ChatSummary:
    id: int
    name: str
    last_update: datetime

    @property
    def preview(self):
        return (
            f"| {self.last_update.strftime('%d%m%Y %H:%M:%S')} | {self.id}: {self.name}"
        )

    @property
    def id_for_ui(self):
        return f"chat-list-item-{self.id}"


@dataclass
class ChatManager:
    @classmethod
    async def aget_all_for_project(cls, project_id: int):
        async for c in ReadingPalChat.aget_all(project_id):
            yield ChatSummary(id=c.id, name=c.name, last_update=c.date_updated)

    @classmethod
    async def aadd_chat(cls, project_id: int) -> ReadingPalChat | None:
        project_config_row = await ProjectConfigRow.aget_by_project(project_id)
        if not project_config_row:
            return
        res = await ReadingPalChat.acreate(project_id)
        await EventLogRows.acreate(
            project_id=project_id,
            type=EventLogRows.EventType.CHAT_CREATED,
            entity_id=res.id,
        )
        return res
