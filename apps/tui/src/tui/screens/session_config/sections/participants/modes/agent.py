from typing import cast

from api_client.models import AIModelRead, ReasoningEffort
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input, Select, TextArea

from tui.screens.session_config.sections.participants.state import AgentParticipantFormState
from tui.screens.session_config.sections.state import SelectValue
from tui.shared.textual import on
from tui.widgets.forms.field import field

# TODO: Can these strings be part of the schema metadata as well? to DRY
REASONING_EFFORT_OPTIONS = [
    ("None", ReasoningEffort.NONE),
    ("Low", ReasoningEffort.LOW),
    ("Medium", ReasoningEffort.MEDIUM),
    ("High", ReasoningEffort.HIGH),
]


class AgentParticipantFields(Container):
    DEFAULT_CSS = """
    AgentParticipantFields {
        height: auto;
        width: 100%;
    }

    AgentParticipantFields .agent-system-prompt {
        height: 5;
    }
    """

    can_focus = False

    def __init__(
        self,
        *,
        initial_state: AgentParticipantFormState,
        models: list[AIModelRead],
        read_only: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._initial_state = initial_state
        self._models = models
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            SCHEMA_FIELDS["AgentParticipantCreate"]["name"]["title"],
            Input(self._initial_state.name, disabled=self._read_only, classes="participant-name"),
            helper_text=SCHEMA_FIELDS["AgentParticipantCreate"]["name"]["description"],
        )
        yield field(
            SCHEMA_FIELDS["AgentParticipantCreate"]["model"]["title"],
            Select(
                [(model.label, model.id) for model in self._models],
                value=self._initial_state.model,
                allow_blank=True,
                disabled=self._read_only,
                classes="agent-model",
            ),
            helper_text=SCHEMA_FIELDS["AgentParticipantCreate"]["model"]["description"],
        )
        yield field(
            SCHEMA_FIELDS["AgentParticipantCreate"]["reasoning_effort"]["title"],
            Select(
                REASONING_EFFORT_OPTIONS,
                value=self._initial_state.reasoning_effort,
                allow_blank=False,
                disabled=self._read_only or not self._selected_model_supports_reasoning(self._initial_state.model),
                classes="agent-reasoning-effort",
            ),
            helper_text=SCHEMA_FIELDS["AgentParticipantCreate"]["reasoning_effort"]["description"],
        )
        yield field(
            SCHEMA_FIELDS["AgentParticipantCreate"]["system_prompt"]["title"],
            TextArea(
                self._initial_state.system_prompt,
                disabled=self._read_only,
                read_only=self._read_only,
                classes="agent-system-prompt",
            ),
            helper_text=SCHEMA_FIELDS["AgentParticipantCreate"]["system_prompt"]["description"],
        )

    @on(Select.Changed, ".agent-model")
    def handle_model_changed(self, event: Select.Changed) -> None:
        reasoning_select = self.query_one(".agent-reasoning-effort", Select)
        supports_reasoning = self._selected_model_supports_reasoning(cast(SelectValue, event.value))
        reasoning_select.disabled = self._read_only or not supports_reasoning
        if not supports_reasoning:
            reasoning_select.value = ReasoningEffort.NONE

    def form_state(self) -> AgentParticipantFormState:
        model_select = self.query_one(".agent-model", Select)
        return AgentParticipantFormState(
            name=self.query_one(".participant-name", Input).value,
            model=cast(SelectValue, model_select.value),
            reasoning_effort=ReasoningEffort(self.query_one(".agent-reasoning-effort", Select).value),
            system_prompt=self.query_one(".agent-system-prompt", TextArea).text,
            key=self._initial_state.key,
        )

    def _selected_model_supports_reasoning(self, model_id: SelectValue) -> bool:
        if not isinstance(model_id, str):
            return False

        return any(model.id == model_id and model.supports_reasoning for model in self._models)
