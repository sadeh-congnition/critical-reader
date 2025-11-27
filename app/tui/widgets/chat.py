from common.chat_manager import ChatManager
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
)
from tui.models import AppState


class ChatListItem(ListItem):
    class Selected(Message):
        def __init__(self, id: str):
            self.chat_id_for_ui = id
            super().__init__()

    def key_enter(self, event: events.Key) -> None:
        raise KeyboardInterrupt(event)


class ChatList(Widget):
    def compose(self) -> ComposeResult:
        yield ListView(id="chat-summary-list")

    async def on_mount(self):
        tui_list_items = self.query_one("#chat-summary-list", ListView)
        async for c in ChatManager.aget_all_for_project(
            AppState.active_project.id_in_db
        ):
            tui_list_items.append(ChatListItem(Label(c.preview), id=c.id_for_ui))

    async def on_list_view_selected(self, item):
        self.post_message(ChatListItem.Selected(item.item.id))


class ChatDetailsView(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="chat_user_input_box"):
            yield Input(placeholder="Enter message", id="chat_user_input_message")
        yield Footer()

    def on_mount(self):
        self.title = "Chat Details"
