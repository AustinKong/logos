from typing import cast

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input, Select, TextArea

from tui.screens.session_config.models import ModelOptionState
from tui.screens.session_config.sections.participants.state import AgentParticipantFormState
from tui.screens.session_config.sections.state import SelectValue
from tui.widgets.forms import field


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
        model_options: list[ModelOptionState],
        read_only: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._initial_state = initial_state
        self._model_options = model_options
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field("Name", Input(self._initial_state.name, disabled=self._read_only, classes="participant-name"))
        yield field(
            "Model",
            Select(
                [(model.label, model.id) for model in self._model_options],
                value=self._initial_state.model,
                allow_blank=True,
                disabled=self._read_only,
                classes="agent-model",
            ),
        )
        yield field(
            "System prompt",
            TextArea(
                self._initial_state.system_prompt,
                disabled=self._read_only,
                read_only=self._read_only,
                classes="agent-system-prompt",
            ),
        )

    def form_state(self) -> AgentParticipantFormState:
        model_select = self.query_one(".agent-model", Select)
        return AgentParticipantFormState(
            name=self.query_one(".participant-name", Input).value,
            model=cast(SelectValue, model_select.value),
            system_prompt=self.query_one(".agent-system-prompt", TextArea).text,
            key=self._initial_state.key,
        )
