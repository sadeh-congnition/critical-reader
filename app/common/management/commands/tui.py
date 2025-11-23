import djclick as click
from textual import widgets
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
    Project,
)
from tui.widgets.project import ProjectView, ProjectDetails
from tui.models import AppState

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
        self.projects = await ProjectRow.aget_all()
        for c in self.projects:
            await self.mount(ProjectDetails(id=c.id_for_ui))
            await self.mount(Rule())

        for c in self.projects:
            data_table = self.query_one(f"#{c.id_for_ui}", ProjectDetails)
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
        project: Project = await project_row.ato_obj()
        self.mount(ProjectDetails(id=project.id_for_ui))
        data_table = self.query_one(f"#{project.id_for_ui}", ProjectDetails)
        data_table.make_rows(project)
        self.mount(Rule())

    def on_project_details_selected(self, message: ProjectDetails.Selected):
        project_id = message.project_id
        AppState.active_project_id = project_id
        self.push_screen("project-view")


@click.command()
def command():
    app = CriticalReaderTUIApp()
    event = app.run()
    print(event)
