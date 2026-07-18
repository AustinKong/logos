from api_client.models import AILanguageModelRead
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import Container

from tui.screens.participant_editor.models import ParticipantsFormState
from tui.screens.session_config.sections.resolution.models import JuryResolutionFormState
from tui.widgets.forms.field import field
from tui.widgets.participants_table import ParticipantsTable


class JuryResolutionFields(Container):
    DEFAULT_CSS = """
    JuryResolutionFields {
        height: auto;
        width: 100%;
    }
    """

    can_focus = False

    def __init__(
        self,
        *,
        initial_state: JuryResolutionFormState,
        models: list[AILanguageModelRead],
        read_only: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._jurors = initial_state.jurors
        self._models = models
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            SCHEMA_FIELDS["JuryResolutionConfigCreate"]["jurors"]["title"],
            ParticipantsTable(
                initial_state=ParticipantsFormState(participants=self._jurors),
                models=self._models,
                allow_multiple=True,
                read_only=self._read_only,
            ),
            helper_text=SCHEMA_FIELDS["JuryResolutionConfigCreate"]["jurors"]["description"],
        )

    def form_state(self) -> JuryResolutionFormState:
        return JuryResolutionFormState(
            jurors=self.query_one(ParticipantsTable).form_state().participants,
        )
