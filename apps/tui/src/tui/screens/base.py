from abc import ABCMeta, abstractmethod

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen

from tui.widgets.footer import Footer
from tui.widgets.header import Header


class BaseScreenMeta(type(Screen), ABCMeta):
    pass


class BaseScreen(Screen[None], metaclass=BaseScreenMeta):
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
            yield from self.compose_content()
        yield Footer()

    @abstractmethod
    def compose_content(self) -> ComposeResult:
        pass
