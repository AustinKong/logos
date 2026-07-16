from api_client.models import AILanguageModelRead
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import Container

from tui.screens.participant_editor.models import ParticipantsFormState
from tui.screens.session_config.sections.resolution.models import JudgeResolutionFormState
from tui.widgets.forms.field import field
from tui.widgets.participants_table import ParticipantsTable


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
        models: list[AILanguageModelRead],
        read_only: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._judge = initial_state.judge
        self._models = models
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            SCHEMA_FIELDS["JudgeResolutionConfigCreate"]["judge"]["title"],
            ParticipantsTable(
                initial_state=ParticipantsFormState(participants=[self._judge]),
                models=self._models,
                allow_multiple=False,
                read_only=self._read_only,
            ),
            helper_text=SCHEMA_FIELDS["JudgeResolutionConfigCreate"]["judge"]["description"],
        )

    def form_state(self) -> JudgeResolutionFormState:
        return JudgeResolutionFormState(
            judge=self.query_one(ParticipantsTable).form_state().participants[0],
        )
