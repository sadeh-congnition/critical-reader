from dataclasses import dataclass
from common.project_manager import Project
from common.models import ReadingPalChat


@dataclass
class AppState:
    active_project: Project
    active_chat: ReadingPalChat

    @classmethod
    def set_active_chat(cls, chat: ReadingPalChat):
        cls.active_chat = chat

    @classmethod
    def set_active_project(cls, chat: Project):
        cls.active_project = chat
