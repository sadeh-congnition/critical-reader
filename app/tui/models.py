from dataclasses import dataclass
from common.project_manager import Project


@dataclass
class AppState:
    active_project: Project
