from common.chat_manager import ChatManager
from django.utils import timezone
from textual.reactive import reactive
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
    time = reactive(0.0)

    def compose(self) -> ComposeResult:
        yield ListView(id="chat-summary-list")

    async def on_mount(self):
        self.set_interval(3, self.update_time)
        await self.apopulate_chat_summary_list()

    async def apopulate_chat_summary_list(self):
        tui_list_items = self.query_one("#chat-summary-list", ListView)
        async for c in ChatManager.aget_all_for_project(
            AppState.active_project.id_in_db
        ):
            tui_list_items.append(ChatListItem(Label(c.preview), id=c.id_for_ui))

    async def on_list_view_selected(self, item):
        self.post_message(ChatListItem.Selected(item.item.id))

    def update_time(self):
        self.time = timezone.now()

    async def watch_time(self):
        tui_list_items = self.query_one("#chat-summary-list", ListView)
        await tui_list_items.clear()
        await self.apopulate_chat_summary_list()


class ChatDetailsView(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("q", "quit_app", "Quit app"),
    ]

    def action_quit_app(self):
        self.app.exit()

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="chat_user_input_box"):
            yield Input(placeholder="Enter message", id="chat_user_input_message")
        yield Footer()

    def on_mount(self):
        self.title = "Chat Details"

    async def on_input_submitted(self, event):
        djllm_chat = AppState.active_djllm_chat
        first_user_msg = djllm_chat.create_user_message(
            text=event.value,
        )

        model_name = "ollama_chat/qwen3:4b"

        ai_msg: Message
        user_msg: Message
        llm_call: LLMCall

        ai_msg, second_user_msg, llm_call = djllm_chat.send_user_msg_to_llm(
            model_name=model_name,
            text=event.value,
        )
        raise KeyboardInterrupt(event.value)
