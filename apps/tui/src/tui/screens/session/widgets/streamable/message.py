from datetime import datetime
from uuid import UUID

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static
from tui.shared.colors import color_from_id


class Message(Vertical):
    DEFAULT_CSS = """
    Message {
        height: auto;
        width: 100%;
        margin-bottom: 1;
        padding: 0;
    }

    Message .message-sender {
        height: auto;
        width: 100%;
        text-style: bold;
    }

    Message .message-content {
        height: auto;
        width: 100%;
    }

    Message .message-time {
        height: auto;
        width: 100%;
        color: $text-secondary
    }
    """

    def __init__(self, *, content: str = "", sender_id: UUID, sender_name: str, timestamp: datetime) -> None:
        super().__init__(classes="message")
        self._content = content
        self._sender_id = sender_id
        self._sender_name = sender_name
        self._timestamp = timestamp

        self._content_widget: Static | None = None

    def compose(self) -> ComposeResult:
        sender = Static(self._sender_name, classes="message-sender")
        accent = self.app.theme_variables["accent"]
        sender.styles.color = color_from_id(self._sender_id, accent)
        yield sender

        self._content_widget = Static(self._content, classes="message-content")
        yield self._content_widget

        yield Static(self._timestamp.strftime("%H:%M"), classes="message-time")

    def append_content(self, content: str) -> None:
        self.set_content(self._content + content)

    def set_content(self, content: str) -> None:
        self._content = content
        if self._content_widget is not None:
            self._content_widget.update(self._content)
