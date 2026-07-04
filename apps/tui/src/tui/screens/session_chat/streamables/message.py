from api_client.models.message_started_event_read import MessageStartedEventRead
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static
from tui.shared.colors import color_from_id
from tui.shared.time import format_time


class Message(Vertical):
    DEFAULT_CSS = """
    Message {
        height: auto;
        width: 100%;
        margin-bottom: 1;
        padding: 0;
    }

    Message .message-sender {
        text-style: bold;
    }
    """

    def __init__(self, *, event: MessageStartedEventRead, content: str = "") -> None:
        super().__init__(classes="message")
        self._content = content
        self._event = event

        self._content_widget: Static | None = None

    def compose(self) -> ComposeResult:
        sender = Static(self._event.sender.name, classes="message-sender")
        accent = self.app.theme_variables["accent"]
        sender.styles.color = color_from_id(self._event.sender.id, accent)
        yield sender

        self._content_widget = Static(self._content)
        yield self._content_widget

        yield Static(format_time(self._event.created_at), classes="muted")

    def append_content(self, content: str) -> None:
        self.set_content(self._content + content)

    def set_content(self, content: str) -> None:
        self._content = content
        if self._content_widget is not None:
            self._content_widget.update(self._content)
