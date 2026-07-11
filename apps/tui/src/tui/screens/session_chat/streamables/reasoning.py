from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class Reasoning(Vertical):
    DEFAULT_CSS = """
    Reasoning {
        height: auto;
        width: 100%;
        padding: 0;
    }

    Reasoning .reasoning-content {
        height: auto;
        width: 100%;
        text-style: italic;
    }
    """

    def __init__(self, *, content: str = "") -> None:
        # TODO: FIXME: Same as message.py
        super().__init__(classes="reasoning")
        self._content = content

        self._content_widget: Static | None = None

    def compose(self) -> ComposeResult:
        self._content_widget = Static(self._content, classes="reasoning-content muted")
        yield self._content_widget

    def append_content(self, content: str) -> None:
        self.set_content(self._content + content)

    def set_content(self, content: str) -> None:
        self._content = content
        if self._content_widget is not None:
            self._content_widget.update(self._content)
