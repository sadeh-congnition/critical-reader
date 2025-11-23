from dataclasses import dataclass

from .models import ReadingPalChat
from configuration.models import ProjectConfigRow


@dataclass
class ChatSummary:
    id: int
    name: str

    @property
    def preview(self):
        return f"{self.name}"


@dataclass
class ChatManager:
    @classmethod
    async def aget_all_for_project(cls, project_id: int):
        async for c in ReadingPalChat.aget_all(project_id):
            yield ChatSummary(id=c.id, name=c.name)

    @classmethod
    async def aadd_chat(cls, project_id: int) -> ReadingPalChat | None:
        project_config_row = await ProjectConfigRow.aget_by_project(project_id)
        if not project_config_row:
            return
        res = await ReadingPalChat.acreate(project_id)
        return res
