import djclick as click
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import (
    Footer,
    Header,
    Rule,
)

from configuration.models import create_default_rows
from common.models import (
    ProjectRow,
)
from common.project_manager import Project, ProjectManager
from tui.widgets.project import ProjectView, ProjectSummary

create_default_rows()


class CriticalReaderTUIApp(App):
    """The TUI for Critical Reader"""

    CSS_PATH = "tui_styling.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit_app", "Quit app"),
        ("s", "create_project", "Start a new project"),
    ]
    SCREENS = {"project-view": ProjectView}

    project_added = reactive("0")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    async def on_mount(self):
        async for c in ProjectManager.aget_all():
            await self.mount(ProjectSummary(id=c.id_for_ui))
            await self.mount(Rule())

        async for c in ProjectManager.aget_all():
            data_table = self.query_one(f"#{c.id_for_ui}", ProjectSummary)
            data_table.make_rows(c)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit_app(self):
        self.exit()

    async def action_create_project(self):
        project_row = await ProjectRow.acreate()
        project: Project = await Project.acreate_from_db_row(project_row)
        self.mount(ProjectSummary(id=project.id_for_ui))
        data_table = self.query_one(f"#{project.id_for_ui}", ProjectSummary)
        data_table.make_rows(project)
        self.mount(Rule())

    async def on_project_summary_selected(self, message: ProjectSummary.Selected):
        project_ui_id = message.project_id
        await ProjectManager.aset_app_state(Project.db_id_from_ui_id(project_ui_id))
        self.push_screen("project-view")


@click.command()
def command():
    app = CriticalReaderTUIApp()
    event = app.run()
    print(event)
