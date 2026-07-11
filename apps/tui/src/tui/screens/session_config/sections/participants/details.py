from api_client.models import AILanguageModelRead
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input

from tui.screens.session_config.sections.participants.messages import ParticipantNameChanged
from tui.screens.session_config.sections.participants.models import (
    ParticipantFormState,
    participant_form_state,
)
from tui.screens.session_config.sections.participants.modes.participant import ParticipantFields
from tui.screens.session_config.sections.state import state_or_default
from tui.shared.textual import on


class ParticipantDetails(VerticalScroll):
    DEFAULT_CSS = """
    ParticipantDetails {
        padding: 0;
        overflow-y: auto;
    }

    ParticipantDetails Select > SelectOverlay {
        constrain: inside inside;
    }
    """

    can_focus = False

    def __init__(
        self,
        *,
        participant_index: int,
        initial_state: ParticipantFormState,
        models: list[AILanguageModelRead],
        read_only: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._participant_index = participant_index
        self._participant_key = initial_state.key
        self._initial_state = initial_state
        self._models = models
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield ParticipantFields(
            initial_state=state_or_default(
                self._initial_state,
                ParticipantFormState,
                participant_form_state(self._participant_index, key=self._participant_key),
            ),
            models=self._models,
            read_only=self._read_only,
            id="participant-fields",
            schema_name="DebaterParticipantCreate",
        )

    @on(Input.Changed, ".participant-name")
    def handle_participant_name_changed(self, event: Input.Changed) -> None:
        self.post_message(ParticipantNameChanged(self._participant_key, event.value))

    def form_state(self) -> ParticipantFormState:
        return self.query_one("#participant-fields", ParticipantFields).form_state()

    @property
    def participant_key(self) -> str:
        return self._participant_key
