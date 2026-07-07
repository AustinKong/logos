from api_client.models import AIModelRead
from textual.app import ComposeResult
from textual.containers import Container

from tui.screens.session_config.sections.participants.modes.participant import ParticipantFields
from tui.screens.session_config.sections.resolution.models import JudgeResolutionFormState


class JudgeResolutionFields(Container):
    DEFAULT_CSS = """
    JudgeResolutionFields {
        height: auto;
        width: 100%;
    }
    """

    can_focus = False

    def __init__(
        self,
        *,
        initial_state: JudgeResolutionFormState,
        models: list[AIModelRead],
        read_only: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._initial_state = initial_state
        self._models = models
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield ParticipantFields(
            initial_state=self._initial_state.judge,
            models=self._models,
            schema_name="JudgeParticipantCreate",
            read_only=self._read_only,
            id="judge-participant-fields",
        )

    def form_state(self) -> JudgeResolutionFormState:
        return JudgeResolutionFormState(
            judge=self.query_one("#judge-participant-fields", ParticipantFields).form_state(),
        )
