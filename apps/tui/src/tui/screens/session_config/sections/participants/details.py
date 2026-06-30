from typing import cast

from api_client.models import ParticipantType
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import ContentSwitcher, Input, Select

from tui.screens.session_config.models import ModelOptionState
from tui.screens.session_config.sections.participants.messages import ParticipantNameChanged
from tui.screens.session_config.sections.participants.modes.agent import AgentParticipantFields
from tui.screens.session_config.sections.participants.modes.user import UserParticipantFields
from tui.screens.session_config.sections.participants.state import (
    AgentParticipantFormState,
    ParticipantFormState,
    UserParticipantFormState,
    agent_participant_form_state,
    user_participant_form_state,
)
from tui.screens.session_config.sections.state import state_or_default
from tui.shared.textual import on
from tui.widgets.forms import field

PARTICIPANT_TYPE_OPTIONS = [
    ("Agent", ParticipantType.AGENT),
    ("User", ParticipantType.USER),
]
PARTICIPANT_TYPE_CONTENT_IDS = {
    ParticipantType.AGENT: "agent-participant-fields",
    ParticipantType.USER: "user-participant-fields",
}


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
        model_options: list[ModelOptionState],
        read_only: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._participant_index = participant_index
        self._participant_key = initial_state.key
        self._initial_state = initial_state
        self._model_options = model_options
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            "Role",
            Select(
                PARTICIPANT_TYPE_OPTIONS,
                value=self._initial_state.type_,
                allow_blank=False,
                disabled=self._read_only,
                classes="participant-role",
            ),
        )
        yield ContentSwitcher(
            UserParticipantFields(
                initial_state=state_or_default(
                    self._initial_state,
                    UserParticipantFormState,
                    user_participant_form_state(self._participant_index, key=self._participant_key),
                ),
                read_only=self._read_only,
                id=self._content_id(ParticipantType.USER),
            ),
            AgentParticipantFields(
                initial_state=state_or_default(
                    self._initial_state,
                    AgentParticipantFormState,
                    agent_participant_form_state(self._participant_index, key=self._participant_key),
                ),
                model_options=self._model_options,
                read_only=self._read_only,
                id=self._content_id(ParticipantType.AGENT),
            ),
            initial=self._content_id(self._initial_state.type_),
            classes="participant-fields",
        )

    @on(Select.Changed)
    def handle_participant_role_changed(self, event: Select.Changed) -> None:
        if not event.select.has_class("participant-role"):
            return

        participant_type = cast(ParticipantType, event.value)
        switcher = self.query_one(".participant-fields", ContentSwitcher)
        switcher.current = self._content_id(participant_type)
        self.post_message(ParticipantNameChanged(self._participant_key, self.form_state().name))

    @on(Input.Changed, ".participant-name")
    def handle_participant_name_changed(self, event: Input.Changed) -> None:
        switcher = self.query_one(".participant-fields", ContentSwitcher)
        # Both mode widgets stay mounted; only the active mode should label the table row.
        if not any(ancestor.id == switcher.current for ancestor in event.input.ancestors):
            return

        self.post_message(ParticipantNameChanged(self._participant_key, event.value))

    def form_state(self) -> ParticipantFormState:
        role_select = self.query_one(".participant-role", Select)
        match cast(ParticipantType, role_select.value):
            case ParticipantType.AGENT:
                return self.query_one(
                    f"#{self._content_id(ParticipantType.AGENT)}", AgentParticipantFields
                ).form_state()
            case ParticipantType.USER:
                return self.query_one(f"#{self._content_id(ParticipantType.USER)}", UserParticipantFields).form_state()

    @property
    def participant_key(self) -> str:
        return self._participant_key

    def _content_id(self, participant_type: ParticipantType) -> str:
        return f"participant-{self._participant_key}-{PARTICIPANT_TYPE_CONTENT_IDS[participant_type]}"
