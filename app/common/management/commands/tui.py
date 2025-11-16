import djclick as click
from textual.reactive import reactive
from textual.message import Message
from textual import events
from textual.widgets import Footer, Header
from textual.app import App, ComposeResult
from textual.widgets import (
    DataTable,
    Rule,
    Footer,
    Header,
)
from common.models import (
    Conversation,
    ConversationTable,
    aget_conversations,
)


class ConversationDetails(DataTable):
    class Selected(Message):
        def __init__(self, id: str):
            self.conversation_id = id
            super().__init__()

    def on_mount(self):
        self.add_columns("ID", "Resources", "Status")

    def make_rows(self, c: Conversation):
        rows = []
        if len(c.resources) == 0:
            rows = [[c.id_for_ui, "Add resources!", c.status]]
        else:
            for i, r in enumerate(c.resources):
                if i == 0:
                    row = [c.id_for_ui, f"{r.name}: {r.status}", c.status]
                else:
                    row = ["", f"{r.name}: {r.status}", ""]
                rows.append(row)
        for r in rows:
            self.add_row(*r)

    def key_enter(self, event: events.Key) -> None:
        self.post_message(self.Selected(self.id))


class CriticalReaderTUIApp(App):
    """The TUI for Critical Reader"""

    CSS_PATH = "tui_styling.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit_app", "Quit"),
        ("s", "create_conversation", "Start a new conversation"),
    ]

    conversation_added = reactive("0")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    async def on_mount(self):
        self.conversations = await aget_conversations()
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
        new_convo_db_row = await ConversationTable.acreate()
        convo = await new_convo_db_row.conversation()
        self.mount(ConversationDetails(id=convo.id_for_ui))
        data_table = self.query_one(f"#{convo.id_for_ui}", ConversationDetails)
        data_table.make_rows(convo)
        self.mount(Rule())

    def on_conversation_details_selected(self, message: ConversationDetails.Selected):
        conv_id = message.conversation_id
        # self.mount()


@click.command()
def command():
    app = CriticalReaderTUIApp()
    event = app.run()
    print(event)
