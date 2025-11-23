from textual.widgets import Static
from textual.screen import ModalScreen
from textual.app import ComposeResult


class ConfigMissing(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Static(
            "[bold][red]No project config found. Add it using the Django admin website![/]"
        )

    def on_key(self):
        self.app.pop_screen()
