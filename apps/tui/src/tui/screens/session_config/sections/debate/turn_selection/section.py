from typing import assert_never

from api_client.models import TurnSelectionMode
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Select
from tui.screens.session_config.sections.debate.turn_selection.models import (
    RoundRobinTurnSelectionFormState,
    ShuffledTurnSelectionFormState,
    TurnSelectionFormState,
)
from tui.widgets.forms.select_field import SelectField, SelectOption

TURN_SELECTION_MODE_OPTIONS = [
    SelectOption(
        SCHEMA_FIELDS["RoundRobinTurnSelectionConfigCreate"]["mode"]["title"],
        TurnSelectionMode.ROUND_ROBIN,
        SCHEMA_FIELDS["RoundRobinTurnSelectionConfigCreate"]["mode"]["description"],
    ),
    SelectOption(
        SCHEMA_FIELDS["ShuffledTurnSelectionConfigCreate"]["mode"]["title"],
        TurnSelectionMode.SHUFFLED,
        SCHEMA_FIELDS["ShuffledTurnSelectionConfigCreate"]["mode"]["description"],
    ),
]


class TurnSelectionSection(Container):
    DEFAULT_CSS = """
    TurnSelectionSection {
        height: auto;
        width: 100%;
    }
    """

    can_focus = False

    def __init__(self, *, initial_state: TurnSelectionFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield SelectField(
            SCHEMA_FIELDS["DebateConfigCreate"]["turn_selection"]["title"],
            options=TURN_SELECTION_MODE_OPTIONS,
            value=self._initial_state.mode,
            allow_blank=False,
            disabled=self._read_only,
        )

    def form_state(self) -> TurnSelectionFormState:
        mode_select = self.query_one(Select)
        match TurnSelectionMode(mode_select.value):
            case TurnSelectionMode.ROUND_ROBIN:
                return RoundRobinTurnSelectionFormState()
            case TurnSelectionMode.SHUFFLED:
                return ShuffledTurnSelectionFormState()
            case _ as never:
                assert_never(never)
