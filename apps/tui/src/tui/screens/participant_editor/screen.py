from typing import cast

from api_client.models import AILanguageModelRead, ReasoningEffort, Verbosity
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, Select, TextArea

from tui.screens.participant_editor.models import ParticipantFormState
from tui.screens.session_config.sections.state import SelectValue
from tui.shared.textual import on
from tui.widgets.forms.field import field
from tui.widgets.screens.base_modal_screen import BaseModalScreen

REASONING_EFFORT_OPTIONS = [
    ("None", ReasoningEffort.NONE),
    ("Low", ReasoningEffort.LOW),
    ("Medium", ReasoningEffort.MEDIUM),
    ("High", ReasoningEffort.HIGH),
]
VERBOSITY_OPTIONS = [
    ("Low", Verbosity.LOW),
    ("Medium", Verbosity.MEDIUM),
    ("High", Verbosity.HIGH),
]


class ParticipantEditorModal(BaseModalScreen[ParticipantFormState]):
    DEFAULT_CSS = """
    .base-modal-screen.participant-editor-modal {
        background: transparent;
    }

    ParticipantEditorModal .participant-system-prompt {
        height: 5;
    }
    """

    DEFAULT_CLASSES = "base-modal-screen participant-editor-modal"
    SCOPED_CSS = False

    BINDINGS = [("escape", "close", "Close")]

    def __init__(
        self,
        *,
        initial_state: ParticipantFormState,
        models: list[AILanguageModelRead],
        read_only: bool = False,
    ) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._models = models
        self._read_only = read_only
        self.modal_title = "View participant" if read_only else "Edit participant"

    def compose_content(self) -> ComposeResult:
        with VerticalScroll(can_focus=False):
            yield field(
                SCHEMA_FIELDS["ParticipantCreate"]["name"]["title"],
                Input(self._initial_state.name, disabled=self._read_only, classes="participant-name"),
                helper_text=SCHEMA_FIELDS["ParticipantCreate"]["name"]["description"],
            )
            yield field(
                SCHEMA_FIELDS["ParticipantCreate"]["model"]["title"],
                Select(
                    [(model.label, model.id) for model in self._models],
                    value=self._initial_state.model,
                    allow_blank=True,
                    disabled=self._read_only,
                    classes="participant-model",
                ),
                helper_text=SCHEMA_FIELDS["ParticipantCreate"]["model"]["description"],
            )
            yield field(
                SCHEMA_FIELDS["ParticipantCreate"]["reasoning_effort"]["title"],
                Select(
                    REASONING_EFFORT_OPTIONS,
                    value=self._initial_state.reasoning_effort,
                    allow_blank=False,
                    disabled=self._read_only or not self._selected_model_supports_reasoning(self._initial_state.model),
                    classes="participant-reasoning-effort",
                ),
                helper_text=SCHEMA_FIELDS["ParticipantCreate"]["reasoning_effort"]["description"],
            )
            yield field(
                SCHEMA_FIELDS["ParticipantCreate"]["verbosity"]["title"],
                Select(
                    VERBOSITY_OPTIONS,
                    value=self._initial_state.verbosity,
                    allow_blank=False,
                    disabled=self._read_only,
                    classes="participant-verbosity",
                ),
                helper_text=SCHEMA_FIELDS["ParticipantCreate"]["verbosity"]["description"],
            )
            yield field(
                SCHEMA_FIELDS["ParticipantCreate"]["temperature"]["title"],
                Input(
                    self._initial_state.temperature,
                    type="number",
                    disabled=self._read_only,
                    classes="participant-temperature",
                ),
                helper_text=SCHEMA_FIELDS["ParticipantCreate"]["temperature"]["description"],
            )
            yield field(
                SCHEMA_FIELDS["ParticipantCreate"]["system_prompt"]["title"],
                TextArea(
                    self._initial_state.system_prompt,
                    disabled=self._read_only,
                    read_only=self._read_only,
                    classes="participant-system-prompt",
                ),
                helper_text=SCHEMA_FIELDS["ParticipantCreate"]["system_prompt"]["description"],
            )

    @on(Select.Changed, ".participant-model")
    def handle_model_changed(self, event: Select.Changed) -> None:
        reasoning_select = self.query_one(".participant-reasoning-effort", Select)
        supports_reasoning = self._selected_model_supports_reasoning(cast(SelectValue, event.value))
        reasoning_select.disabled = self._read_only or not supports_reasoning
        if not supports_reasoning:
            reasoning_select.value = ReasoningEffort.NONE

    def action_close(self) -> None:
        model_select = self.query_one(".participant-model", Select)
        self.dismiss(
            ParticipantFormState(
                name=self.query_one(".participant-name", Input).value,
                model=cast(SelectValue, model_select.value),
                reasoning_effort=ReasoningEffort(self.query_one(".participant-reasoning-effort", Select).value),
                verbosity=Verbosity(self.query_one(".participant-verbosity", Select).value),
                temperature=self.query_one(".participant-temperature", Input).value,
                system_prompt=self.query_one(".participant-system-prompt", TextArea).text,
                key=self._initial_state.key,
            )
        )

    def _selected_model_supports_reasoning(self, model_id: SelectValue) -> bool:
        if not isinstance(model_id, str):
            return False

        return any(model.id == model_id and model.supports_reasoning for model in self._models)
