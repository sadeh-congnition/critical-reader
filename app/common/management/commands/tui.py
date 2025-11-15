import djclick as click
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


@dataclass
class ConversationStatus:
    status: str
    description: str = ""

    def __str__(self):
        if self.description:
            return f"{self.status}, {self.description}"
        return self.status


@dataclass
class ResourceStatus:
    status: str

    def __str__(self):
        return self.status


@dataclass
class Resource:
    name: str
    status: ResourceStatus


@dataclass
class Conversation:
    id: int | str
    resources: list[Resource]
    status: ConversationStatus

    def __str__(self):
        return f"{self.id}: {str(self.status)}"


def get_conversations():
    return [
        Conversation(
            "c1",
            [
                Resource("Article 1", ResourceStatus("Downloaded")),
                Resource("Article 2", ResourceStatus("Fetching")),
            ],
            ConversationStatus("New", description="Add a resource"),
        ),
        Conversation(
            "c2",
            [Resource("Article 3", ResourceStatus("Downloaded"))],
            ConversationStatus("New"),
        ),
    ]


class ConversationDetails(DataTable):
    class Selected(Message):
        def __init__(self, id: str):
            self.conversation_id = id
            super().__init__()

    def on_mount(self):
        self.add_columns("ID", "Resources", "Status")

    def make_rows(self, c):
        rows = []
        for i, r in enumerate(c.resources):
            if i == 0:
                row = [c.id, f"{r.name}: {r.status}", c.status]
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

        self.conversations = get_conversations()
        for c in self.conversations:
            yield ConversationDetails(id=c.id)
            yield Rule()

    def on_mount(self):
        for c in self.conversations:
            data_table = self.query_one(f"#{c.id}", ConversationDetails)
            data_table.make_rows(c)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_quit_app(self):
        self.exit()

    def on_conversation_details_selected(self, message: ConversationDetails.Selected):
        self.exit(message)


@click.command()
def command():
    app = CriticalReaderTUIApp()
    event = app.run()
    print(event)
    breakpoint()
