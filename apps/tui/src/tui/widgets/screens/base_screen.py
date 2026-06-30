from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, LoadingIndicator

from tui.widgets.header import Header


class BaseScreen(Screen[None]):
    content_loading = reactive(False, recompose=True)

    DEFAULT_CSS = """
    BaseScreen {
        padding: 1;
    }

    .screen-content {
        height: 1fr;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(version="0.0.1")

        with Vertical(classes="screen-content"):
            if self.content_loading:
                yield LoadingIndicator()
            else:
                yield from self.compose_content()
        yield Footer(compact=True, show_command_palette=False)

    def compose_content(self) -> ComposeResult:
        yield from ()
