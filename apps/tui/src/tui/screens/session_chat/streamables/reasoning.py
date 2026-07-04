from api_client.models.reasoning_started_event_read import ReasoningStartedEventRead
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static
from tui.shared.colors import color_from_id


class Reasoning(Vertical):
    DEFAULT_CSS = """
    Reasoning {
        height: auto;
        width: 100%;
        margin-bottom: 1;
        padding: 0;
    }

    Reasoning .reasoning-sender {
        height: auto;
        width: 100%;
        text-style: bold;
    }

    Reasoning .reasoning-content {
        height: auto;
        width: 100%;
        text-style: italic;
    }

    Reasoning .reasoning-time {
        height: auto;
        width: 100%;
    }
    """

    def __init__(self, *, event: ReasoningStartedEventRead, content: str = "") -> None:
        super().__init__(classes="reasoning")
        self._content = content
        self._event = event

        self._content_widget: Static | None = None

    def compose(self) -> ComposeResult:
        sender = Static(self._event.sender.name, classes="reasoning-sender")
        accent = self.app.theme_variables["accent"]
        sender.styles.color = color_from_id(self._event.sender.id, accent)
        yield sender

        self._content_widget = Static(self._content, classes="reasoning-content muted")
        yield self._content_widget

        yield Static(self._event.created_at.strftime("%H:%M"), classes="reasoning-time muted")

    def append_content(self, content: str) -> None:
        self.set_content(self._content + content)

    def set_content(self, content: str) -> None:
        self._content = content
        if self._content_widget is not None:
            self._content_widget.update(self._content)
