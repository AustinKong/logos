from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Rule, Static


class Divider(Horizontal):
    DEFAULT_CSS = """
    Divider {
        height: auto;
        width: 100%;
        align: center middle;
    }

    Divider Rule {
        width: 1fr;
    }

    Divider .divider-label {
        width: auto;
        padding: 1;
        text-style: bold;
    }
    """

    def __init__(self, label: str) -> None:
        super().__init__()
        self._label = label

    def compose(self) -> ComposeResult:
        yield Rule(line_style="heavy")
        yield Static(self._label, classes="divider-label")
        yield Rule(line_style="heavy")
