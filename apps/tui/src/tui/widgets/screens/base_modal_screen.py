from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Footer, LoadingIndicator


class BaseModalScreen[ResultT](ModalScreen[ResultT]):
    DEFAULT_CLASSES = "base-modal-screen"

    SCOPED_CSS = False

    DEFAULT_CSS = """
    .base-modal-screen {
        align: center middle;
        background: $background 80%;
    }

    .base-modal-screen .modal-shell {
        width: 90%;
        height: 90%;
        background: transparent;
        padding: 1;
    }

    .base-modal-screen .modal-panel {
        width: 100%;
        height: 1fr;
        background: transparent;
        border: solid $primary;
        padding: 0 1;
    }
    """

    modal_title = ""
    content_loading = reactive(False, recompose=True)

    def compose(self) -> ComposeResult:
        panel = Container(classes="modal-panel")
        panel.border_title = self.modal_title

        with Container(classes="modal-shell"):
            with panel:
                if self.content_loading:
                    yield LoadingIndicator()
                else:
                    yield from self.compose_content()
            yield Footer(compact=True, show_command_palette=False)

    def compose_content(self) -> ComposeResult:
        yield from ()
