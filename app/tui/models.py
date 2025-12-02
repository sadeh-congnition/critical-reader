from dataclasses import dataclass
from common.project_manager import Project
from common.models import ReadingPalChat
from django_llm_chat.chat import Chat


@dataclass
class AppState:
    active_project: Project
    active_readingpal_chat: ReadingPalChat
    active_djllm_chat: Chat

    @classmethod
    def set_active_djllm_chat(cls, chat: Chat):
        cls.active_djllm_chat = chat

    @classmethod
    def set_active_readingpal_chat(cls, chat: ReadingPalChat):
        cls.active_readingpal_chat = chat

    @classmethod
    def set_active_project(cls, chat: Project):
        cls.active_project = chat
