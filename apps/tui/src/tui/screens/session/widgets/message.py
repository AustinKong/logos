from datetime import datetime

from api_client.models.participant_read import ParticipantRead
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
        color: $foreground 50%;
    }
    """

    def __init__(self, *, content: str, sender: ParticipantRead, timestamp: datetime) -> None:
        super().__init__(classes="message")
        self._content = content
        self._sender = sender
        self._timestamp = timestamp

    def compose(self) -> ComposeResult:
        sender = Static(self._sender.name, classes="message-sender")
        accent = self.app.theme_variables["accent"]
        sender.styles.color = color_from_id(self._sender.id, accent)
        yield sender

        yield Static(self._content, classes="message-content")
        yield Static(self._timestamp.strftime("%H:%M"), classes="message-time")
