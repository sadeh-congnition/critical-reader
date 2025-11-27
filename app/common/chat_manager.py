from dataclasses import dataclass
from datetime import datetime

from .models import ReadingPalChat
from configuration.models import ProjectConfigRow
from common.models import EventLogRows


UI_ID_PREFIX = "chat-list-item"


@dataclass
class ChatSummary:
    id: int
    name: str
    last_update: datetime
    id_for_ui: str

    @property
    def preview(self):
        return (
            f"| {self.last_update.strftime('%d%m%Y %H:%M:%S')} | {self.id}: {self.name}"
        )


@dataclass
class ChatManager:
    @classmethod
    async def aget_all_for_project(cls, project_id: int):
        async for c in ReadingPalChat.aget_all(project_id):
            yield ChatSummary(
                id=c.id,
                name=c.name,
                last_update=c.date_updated,
                id_for_ui=f"{UI_ID_PREFIX}-{c.id}",
            )

    @classmethod
    async def aget_by_ui_id(cls, id_for_ui: str):
        return await ReadingPalChat.aget_by_ui_id(id_for_ui=id_for_ui)

    @classmethod
    async def aadd_chat(cls, project_id: int) -> ReadingPalChat | None:
        project_config_row = await ProjectConfigRow.aget_by_project(project_id)
        if not project_config_row:
            return
        res = await ReadingPalChat.acreate(project_id)
        await res.add_id_for_ui(f"{UI_ID_PREFIX}-{res.id}")
        await EventLogRows.acreate(
            project_id=project_id,
            type=EventLogRows.EventType.CHAT_CREATED,
            entity_id=res.id,
        )
        return res
