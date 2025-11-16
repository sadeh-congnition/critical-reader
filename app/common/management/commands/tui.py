import djclick as click
from textual.css.query import NoMatches
from textual.containers import Grid
from textual.screen import Screen, ModalScreen
from textual.reactive import reactive
from textual.message import Message
from textual import events
from textual.app import App, ComposeResult
from textual.widgets import (
    DataTable,
    Rule,
    Footer,
    Header,
    Static,
    Input,
    Label,
)
from common.models import (
    Conversation,
    ConversationRow,
    create_default_rows,
    ResourceRow,
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
        global ACTIVE_CONVERSATION_ID
        await ResourceRow.acreate(ACTIVE_CONVERSATION_ID, event.value)
        self.app.pop_screen()


class ResroucesList(DataTable):
    def on_mount(self):
        self.add_columns("Name", "Status")

    async def make_rows(self, conversation_id_for_ui):
        resources = await ResourceRow.aget_all_by_conversation_id_for_ui(
            conversation_id_for_ui
        )
        assert len(resources) > 0
        for r in resources:
            if len(r.url) > 50:
                url = r.url[:50] + "..."
            else:
                url = r.url
            self.add_row(url, r.status)


class ConversationView(ModalScreen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("r", "add_resource", "Add resource"),
    ]

    def compose(self) -> ComposeResult:
        global ACTIVE_CONVERSATION_ID
        yield Header()
        yield Footer()
        yield Label("[bold][yellow]Resources[/]")
        yield ResroucesList(id="resources-list")

    async def on_mount(self):
        data_table = self.query_one("#resources-list", ResroucesList)
        await data_table.make_rows(ACTIVE_CONVERSATION_ID)

    def action_add_resource(self):
        self.app.push_screen(CreateResourceView())

    async def on_screen_suspend(self):
        data_table = self.query_one("#resources-list", ResroucesList)
        data_table.remove()

    async def on_screen_resume(self):
        try:
            self.query_one("#resources-list", ResroucesList)
            return
        except NoMatches:
            pass
        await self.mount(ResroucesList(id="resources-list"))
        data_table = self.query_one("#resources-list", ResroucesList)
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
