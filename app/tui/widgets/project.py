from django.utils import timezone
from textual import events
from textual.app import ComposeResult
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Label, RichLog

from tui.widgets.resource import CreateResourceView, ResroucesList
from configuration.models import ProjectConfigRow
from common.models import EventLog, EventLogRows
from common.project_manager import Project
from tui.models import AppState
from tui.widgets.config import ConfigMissing
from tui.widgets.chat import ChatSummaryList, ChatDetailsView
from common.chat_manager import ChatManager


class ProjectSummary(DataTable):
    class Selected(Message):
        def __init__(self, id: str):
            self.project_id = id
            super().__init__()

    def on_mount(self):
        self.add_columns("ID", "Resources", "Configuration")

    def make_rows(self, c: Project):
        rows = []
        if len(c.resources) == 0:
            rows = [[c.id_for_ui, "[bod][red]Add resources![/]", c.config]]
        else:
            for i, r in enumerate(c.resources):
                if i == 0:
                    row = [c.id_for_ui, f"{r.url} -> {r.status}", c.config]
                else:
                    row = ["", f"{r.url} -> {r.status}", ""]
                rows.append(row)
        for r in rows:
            self.add_row(*r)

    def key_enter(self, event: events.Key) -> None:
        self.post_message(self.Selected(self.id))


class ProjectView(ModalScreen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("r", "add_resource", "Add resource"),
        ("c", "add_chat", "Start new chat"),
        ("q", "quit_app", "Quit app"),
    ]

    time = reactive(0.0)

    def action_quit_app(self):
        self.app.exit()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Label("[bold][yellow]Resources[/]")
        yield ResroucesList(id="resources-list")
        yield ChatSummaryList(id="chat-summary-list")
        yield RichLog(id="event-log", markup=True)

    async def on_mount(self):
        self.set_interval(3, self.update_time)
        data_table = self.query_resources_list()
        await data_table.make_rows(AppState.active_project.id_in_db)

    def query_resources_list(self):
        return self.query_one("#resources-list", ResroucesList)

    def update_time(self):
        self.time = timezone.now()

    async def watch_time(self):
        await self.arecreate_resources_table()
        await self.acreate_event_log()

    async def action_add_resource(self):
        project_config_row = await ProjectConfigRow.aget_by_project(
            AppState.active_project.id_in_db
        )
        if not project_config_row:
            self.app.push_screen(ConfigMissing())
        else:
            self.app.push_screen(CreateResourceView())

    async def action_add_chat(self):
        reading_pal_chat_row = await ChatManager.aadd_chat(
            AppState.active_project.id_in_db
        )
        if not reading_pal_chat_row:
            self.app.push_screen(ConfigMissing())
        else:
            self.app.push_screen(ChatDetailsView())

    async def acreate_event_log(self):
        events: list[EventLog] = await EventLogRows.aget_logs_for_project(
            AppState.active_project.id_in_db
        )
        event_log = self.query_one(RichLog)
        event_log.clear()

        event_log.write("[bold][yellow]Project events log:[/]")

        for e in events:
            event_log.write(e.human_readable())

    async def on_screen_suspend(self):
        self.clear_resources_list()

    def clear_resources_list(self):
        data_table = self.query_resources_list()
        data_table.clear()
        return data_table

    async def on_screen_resume(self):
        try:
            self.query_resources_list()
            return
        except NoMatches:
            pass

        await self.arecreate_resources_table()

    async def arecreate_resources_table(self):
        data_table = self.clear_resources_list()
        await data_table.make_rows(AppState.active_project.id_in_db)
