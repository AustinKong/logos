from typing import cast

from api_client.models import ContextConfigRead, ContextMode
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Select

from tui.screens.session_config.sections.context.state import ContextFormState
from tui.widgets.forms import field

CONTEXT_MODE_OPTIONS = [
    ("Full transcript", ContextMode.FULL),
]


class ContextSection(VerticalScroll):
    can_focus = False

    def __init__(self, *, initial_state: ContextFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            "Context mode",
            Select(
                CONTEXT_MODE_OPTIONS,
                value=self._initial_state.mode,
                allow_blank=False,
                disabled=self._read_only,
                id="context-mode",
            ),
        )

    def form_state(self) -> ContextFormState:
        mode_select = self.query_one("#context-mode", Select)
        return ContextConfigRead(mode=cast(ContextMode, mode_select.value))
