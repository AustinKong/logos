from textual.geometry import Spacing
from textual.reactive import reactive
from textual.widgets import Input


class ChatInput(Input):
    shown = reactive(False)

    DEFAULT_CSS = """
    ChatInput {
        width: 1fr;
        border: none;
        background: transparent;
    }
    """

    def on_mount(self) -> None:
        # TODO: What
        self.styles.height = "1fr"
        self.styles.padding = Spacing(0, 0, 0, 0)

    def watch_shown(self, shown: bool) -> None:
        self.display = shown
