import djclick as click
from asgiref.sync import async_to_sync
from textual.message import Message
from textual import events
from dataclasses import dataclass
from textual.widgets import Footer, Header
from textual.app import App, ComposeResult
from textual.widgets import (
    RichLog,
    DataTable,
    Rule,
    Footer,
    Header,
)
from common.models import get_conversations, Conversation


class ConversationDetails(DataTable):
    class Selected(Message):
        def __init__(self, id: str):
            self.conversation_id = id
            super().__init__()

    def on_mount(self):
        self.add_columns("ID", "Resources", "Status")

    def make_rows(self, c: Conversation):
        rows = []
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
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit_app", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    async def on_mount(self):
        self.conversations = await get_conversations()
        for c in self.conversations:
            self.mount(ConversationDetails(id=c.id_for_ui))
            self.mount(Rule())

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

    def on_conversation_details_selected(self, message: ConversationDetails.Selected):
        conv_id = message.conversation_id
        # self.mount()


@click.command()
def command():
    app = CriticalReaderTUIApp()
    event = app.run()
    print(event)
