from django.db import models
from dataclasses import dataclass


@dataclass
class AppState:
    active_project_id: str
