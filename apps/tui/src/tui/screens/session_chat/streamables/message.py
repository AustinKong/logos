from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class Message(Vertical):
    DEFAULT_CSS = """
    Message {
        height: auto;
        width: 100%;
        padding: 0;
    }
    """

    def __init__(self, *, content: str = "") -> None:
        super().__init__(classes="message")
        self._content = content

        self._content_widget: Static | None = None

    def compose(self) -> ComposeResult:
        # TODO: FIXME: Should be able to make this Message(Static) instead
        # of having to make it a vertical wrapping a static
        self._content_widget = Static(self._content)
        yield self._content_widget

    def append_content(self, content: str) -> None:
        self.set_content(self._content + content)

    def set_content(self, content: str) -> None:
        self._content = content
        if self._content_widget is not None:
            self._content_widget.update(self._content)
