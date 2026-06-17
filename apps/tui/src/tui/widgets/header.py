from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Static


class Header(Widget):
    DEFAULT_CSS = """
    Header {
        dock: top;
        height: 1;
        width: 100%;
        background: transparent;
    }

    Header #app-brand,
    Header #app-version {
        height: 1;
        width: auto;
        padding: 0 1;
        background: $primary;
        color: $text;
        text-style: bold;
    }

    Header #app-header-fill {
        height: 1;
        width: 1fr;
        hatch: right $primary;
    }
    """

    def __init__(self, *, version: str) -> None:
        super().__init__()
        self._version = version

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Static("Logos.sh", id="app-brand"),
            Static(id="app-header-fill"),
            Static(f"version {self._version}", id="app-version"),
            id="app-header",
        )
