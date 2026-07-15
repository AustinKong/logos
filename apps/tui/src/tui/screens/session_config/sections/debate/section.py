from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input
from tui.screens.session_config.sections.debate.history.section import HistorySection
from tui.screens.session_config.sections.debate.models import DebateFormState
from tui.screens.session_config.sections.debate.turn_selection.section import TurnSelectionSection
from tui.widgets.forms.field import field


class DebateSection(VerticalScroll):
    can_focus = False

    def __init__(self, *, initial_state: DebateFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            SCHEMA_FIELDS["DebateConfigCreate"]["round_count"]["title"],
            Input(
                self._initial_state.round_count,
                type="integer",
                disabled=self._read_only,
                id="debate-round-count",
            ),
            helper_text=SCHEMA_FIELDS["DebateConfigCreate"]["round_count"]["description"],
        )
        yield HistorySection(
            initial_state=self._initial_state.history,
            read_only=self._read_only,
        )
        yield TurnSelectionSection(
            initial_state=self._initial_state.turn_selection,
            read_only=self._read_only,
        )

    def form_state(self) -> DebateFormState:
        return DebateFormState(
            round_count=self.query_one("#debate-round-count", Input).value,
            participants=self._initial_state.participants,
            turn_selection=self.query_one(TurnSelectionSection).form_state(),
            history=self.query_one(HistorySection).form_state(),
            tools=self._initial_state.tools,
        )
