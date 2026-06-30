from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input

from tui.screens.session_config.sections.participants.state import UserParticipantFormState
from tui.widgets.forms.field import field


class UserParticipantFields(Container):
    DEFAULT_CSS = """
    UserParticipantFields {
        height: auto;
        width: 100%;
    }
    """

    can_focus = False

    def __init__(
        self,
        *,
        initial_state: UserParticipantFormState,
        read_only: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            SCHEMA_FIELDS["UserParticipantCreate"]["name"]["title"],
            Input(self._initial_state.name, disabled=self._read_only, classes="participant-name"),
            helper_text=SCHEMA_FIELDS["UserParticipantCreate"]["name"]["description"],
        )

    def form_state(self) -> UserParticipantFormState:
        return UserParticipantFormState(
            name=self.query_one(".participant-name", Input).value,
            key=self._initial_state.key,
        )
