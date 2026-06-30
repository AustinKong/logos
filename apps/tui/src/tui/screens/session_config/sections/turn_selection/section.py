from typing import cast

from api_client.models import TurnSelectionConfigRead, TurnSelectionMode
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Select

from tui.screens.session_config.sections.turn_selection.state import TurnSelectionFormState
from tui.widgets.forms import field

TURN_SELECTION_MODE_OPTIONS = [
    ("Round robin", TurnSelectionMode.ROUND_ROBIN),
]


class TurnSelectionSection(VerticalScroll):
    can_focus = False

    def __init__(self, *, initial_state: TurnSelectionFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            "Mode",
            Select(
                TURN_SELECTION_MODE_OPTIONS,
                value=self._initial_state.mode,
                allow_blank=False,
                disabled=self._read_only,
            ),
        )

    def form_state(self) -> TurnSelectionFormState:
        mode_select = self.query_one(Select)
        # TODO: Keep this for now, but when i add more fields its not that simple
        return TurnSelectionConfigRead(mode=cast(TurnSelectionMode, mode_select.value))
