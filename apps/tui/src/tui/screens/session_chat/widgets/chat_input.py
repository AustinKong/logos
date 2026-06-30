from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Static


class ChatInput(Horizontal):
    DEFAULT_CSS = """
    ChatInput {
        height: 3;
        width: 100%;
        border: solid $primary;
        background: transparent;
        padding: 0;
    }

    ChatInput Static {
        width: 3;
        height: 1fr;
        content-align: center middle;
        background: transparent;
    }

    ChatInput Input {
        height: 1fr;
        width: 1fr;
        border: none;
        background: transparent;
        padding: 0;
    }
    """

    def __init__(self, *, placeholder: str) -> None:
        super().__init__()
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        yield Static(" → ")
        yield Input(placeholder=self._placeholder)
