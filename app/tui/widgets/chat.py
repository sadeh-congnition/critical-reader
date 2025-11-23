from textual.app import App, ComposeResult
from textual.widgets import LoadingIndicator
from textual.widgets import Footer, Label, ListItem, ListView, Header
from textual.widget import Widget
from textual.screen import Screen

from common.chat_manager import ChatManager


class ChatSummaryList(Widget):
    CSS_PATH = "list_view.tcss"

    def compose(self) -> ComposeResult:
        yield ListView(id="chat-summary-list")

    async def on_mount(self):
        list_items = [
            ListItem(Label(c.preview))
            async for c in ChatManager.aget_all_for_project(1)
        ]

        tui_list_items = self.query_one("#chat-summary-list", ListView)
        for li in list_items:
            tui_list_items.append(li)


class ChatDetailsView(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield ListView(id="chat-messages-list")

    def on_mount(self):
        self.title = "Chat"
