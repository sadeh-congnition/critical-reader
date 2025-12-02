from typing import Self
from dataclasses import dataclass
from datetime import datetime

from django_llm_chat.chat import Chat

from tui.models import AppState

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
        return f"| {self.last_update.strftime('%d/%m/%Y %H:%M:%S')} | {self.id}: {self.name}"


@dataclass
class ChatManager:
    readingpal_chat: ReadingPalChat
    djllmchat: Chat

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
    async def acreate_new(cls, project_id: int) -> Self | None:
        project_config_row = await ProjectConfigRow.aget_by_project(project_id)
        if not project_config_row:
            return

        djllm_chat: Chat = await Chat.acreate()

        res = await ReadingPalChat.acreate(project_id, djllm_chat.chat_db_model)
        await res.aadd_id_for_ui(f"{UI_ID_PREFIX}-{res.id}")

        await djllm_chat.acreate_system_message(
            "You are a helpful companion. Your job is to help me undersand what I'm reading."
        )

        await EventLogRows.acreate(
            project_id=project_id,
            type=EventLogRows.EventType.CHAT_CREATED,
            entity_id=res.id,
        )
        return cls(res, djllm_chat)

    async def aadd_user_msg(self, user_msg: str):
        res = await ReadingPalChat.aadd_user_msg(
            chat_id=AppState.active_chat.id, user_msg=user_msg
        )
        return res

    @classmethod
    async def aada_assistant_msg(cls, user_msg: str):
        res = await ReadingPalChat.aadd_system_msg(
            chat_id=AppState.active_chat.id, user_msg=user_msg
        )
        return res
