from typing import Self
from dataclasses import dataclass

from common.models import Resource, ResourceRow, ProjectRow
from configuration.models import ProjectConfigRow


@dataclass
class Project:
    id_in_db: int
    id_for_ui: str
    resources: list[Resource]
    config: dict

    @classmethod
    async def acreate_from_db_row(cls, project_db_row: ProjectRow) -> Self:
        resources = []
        async for r in ResourceRow.aget_all_by_project_id(project_db_row.id):
            resources.append(Resource(url=r.url, status=r.status))

        config_row = await ProjectConfigRow.aget_by_project(project_db_row.id)
        if config_row:
            config = await config_row.ato_dict()
        else:
            config = {}
        return cls(
            id_in_db=project_db_row.id,
            id_for_ui=cls.make_id_for_ui(project_db_row.id),
            resources=resources,
            config=config,
        )

    def __str__(self):
        return f"{self.id_for_ui}"

    @classmethod
    def make_id_for_ui(cls, db_id) -> str:
        return f"project-{db_id}"

    @classmethod
    def db_id_from_ui_id(cls, ui_id) -> int:
        return int(ui_id.split("project-")[-1])


@dataclass
class ProjectManager:
    @classmethod
    async def acreate_new(cls) -> Project:
        project_row = await ProjectRow.acreate()
        return await Project.acreate_from_db_row(project_row)

    @classmethod
    async def aset_app_state(cls, project_id: int):
        from tui.models import AppState

        project_row = await ProjectRow.aget_by_id(project_id)
        assert project_row

        AppState.active_project = await Project.acreate_from_db_row(project_row)

    @classmethod
    async def aadd_resource(cls, url: str) -> ResourceRow:
        from tui.models import AppState

        project_id = AppState.active_project.id_in_db
        return await ResourceRow.acreate(project_id=project_id, url=url)

    @classmethod
    async def aget_all(cls):
        async for c in ProjectRow.aall():
            yield await Project.acreate_from_db_row(c)
