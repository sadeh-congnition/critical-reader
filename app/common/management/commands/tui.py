import traceback
from loguru import logger
from django.utils import timezone

import djclick as click
from textual._node_list import DuplicateIds
from textual.reactive import reactive
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Grid
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Rule,
    Static,
)

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from common.jobs.job_dispatcher import Event, create_resource_processing_pipeline
from common.models import (
    Conversation,
    ConversationConfigRow,
    ConversationRow,
    ResourceRow,
    create_default_rows,
)

create_default_rows()


class ConversationDetails(DataTable):
    class Selected(Message):
        def __init__(self, id: str):
            self.conversation_id = id
            super().__init__()

    def on_mount(self):
        self.add_columns("ID", "Resources", "Status", "Configuration")

    def make_rows(self, c: Conversation):
        rows = []
        if len(c.resources) == 0:
            rows = [[c.id_for_ui, "Add resources!", c.status, c.config]]
        else:
            for i, r in enumerate(c.resources):
                if i == 0:
                    row = [c.id_for_ui, f"{r.url} -> {r.status}", c.status, c.config]
                else:
                    row = ["", f"{r.url} -> {r.status}", ""]
                rows.append(row)
        for r in rows:
            self.add_row(*r)

    def key_enter(self, event: events.Key) -> None:
        self.post_message(self.Selected(self.id))


class ConversationConfigMissing(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Static(
            "[bold][red]No conversation config found. Add it using the Django admin website![/]"
        )

    def on_key(self):
        self.app.pop_screen()


ACTIVE_CONVERSATION_ID = None


class CreateResourceView(ModalScreen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Close"),
    ]

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Enter URL", id="enter-url"),
            Input(placeholder="Enter URL", id="url-input"),
            id="new-resource",
        )

    async def on_input_submitted(self, event):
        val = URLValidator()
        try:
            val(event.value)
        except ValidationError:
            self.mount(Static("[red]Invalid URL[/]"))
            return

        global ACTIVE_CONVERSATION_ID
        assert ACTIVE_CONVERSATION_ID
        conversation_config_row = (
            await ConversationConfigRow.aget_by_conversation_id_for_ui(
                ACTIVE_CONVERSATION_ID
            )
        )
        if not conversation_config_row:
            self.app.pop_screen()
            self.app.push_screen(ConversationConfigMissing())
            return

        resource = await ResourceRow.acreate(ACTIVE_CONVERSATION_ID, event.value)
        conversation_config = await conversation_config_row.ato_obj()
        try:
            await create_resource_processing_pipeline(
                Event.RESOURCE_CREATED, conversation_config, resource.id
            )
        except Exception:
            await resource.aadd_error(traceback.format_exc())
            raise
        self.app.pop_screen()


class ResroucesList(DataTable):
    def on_mount(self):
        self.add_columns("Name", "Status", "Error")

    async def make_rows(self, conversation_id_for_ui):
        resources = await ResourceRow.aget_all_by_conversation_id_for_ui(
            conversation_id_for_ui
        )
        for r in resources:
            if len(r.url) > 50:
                url = r.url[:50] + "..."
            else:
                url = r.url
            error_msg = r.error_msg.replace("\n", " ") if r.error_msg else ""
            self.add_row(url, r.status, error_msg)


class ConversationView(ModalScreen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("r", "add_resource", "Add resource"),
        ("q", "quit_app", "Quit app"),
    ]

    time = reactive(0.0)

    def action_quit_app(self):
        self.app.exit()

    def compose(self) -> ComposeResult:
        global ACTIVE_CONVERSATION_ID
        yield Header()
        yield Footer()
        yield Label("[bold][yellow]Resources[/]")
        yield ResroucesList(id="resources-list")

    async def on_mount(self):
        self.set_interval(3, self.update_time)
        data_table = self.query_resources_list()

        global ACTIVE_CONVERSATION_ID
        await data_table.make_rows(ACTIVE_CONVERSATION_ID)

    def query_resources_list(self):
        return self.query_one("#resources-list", ResroucesList)

    def update_time(self):
        self.time = timezone.now()

    async def watch_time(self):
        await self.arecreate_resources_table()

    async def action_add_resource(self):
        global ACTIVE_CONVERSATION_ID
        assert ACTIVE_CONVERSATION_ID
        conversation_config_row = (
            await ConversationConfigRow.aget_by_conversation_id_for_ui(
                ACTIVE_CONVERSATION_ID
            )
        )
        if not conversation_config_row:
            self.app.push_screen(ConversationConfigMissing())
        else:
            self.app.push_screen(CreateResourceView())

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

        global ACTIVE_CONVERSATION_ID
        await data_table.make_rows(ACTIVE_CONVERSATION_ID)


class CriticalReaderTUIApp(App):
    """The TUI for Critical Reader"""

    CSS_PATH = "tui_styling.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit_app", "Quit app"),
        ("s", "create_conversation", "Start a new conversation"),
    ]
    SCREENS = {"conversation-view": ConversationView}

    conversation_added = reactive("0")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    async def on_mount(self):
        self.conversations = await ConversationRow.aget_conversations()
        for c in self.conversations:
            await self.mount(ConversationDetails(id=c.id_for_ui))
            await self.mount(Rule())

        for c in self.conversations:
            data_table = self.query_one(f"#{c.id_for_ui}", ConversationDetails)
            data_table.make_rows(c)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit_app(self):
        self.exit()

    async def action_create_conversation(self):
        new_convo_db_row = await ConversationRow.acreate()
        convo = await new_convo_db_row.conversation()
        self.mount(ConversationDetails(id=convo.id_for_ui))
        data_table = self.query_one(f"#{convo.id_for_ui}", ConversationDetails)
        data_table.make_rows(convo)
        self.mount(Rule())

    def on_conversation_details_selected(self, message: ConversationDetails.Selected):
        conv_id = message.conversation_id
        global ACTIVE_CONVERSATION_ID
        ACTIVE_CONVERSATION_ID = conv_id
        self.push_screen("conversation-view")


@click.command()
def command():
    app = CriticalReaderTUIApp()
    event = app.run()
    print(event)
