from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Input, TextArea

from tui.screens.session_config.sections.general.models import GeneralFormState
from tui.widgets.forms.field import field


class GeneralSection(VerticalScroll):
    DEFAULT_CSS = """
    GeneralSection #prompt {
        height: 10;
    }
    """

    can_focus = False

    def __init__(self, *, initial_state: GeneralFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            SCHEMA_FIELDS["SessionConfigCreate"]["prompt"]["title"],
            TextArea(self._initial_state.prompt, disabled=self._read_only, read_only=self._read_only, id="prompt"),
            helper_text=SCHEMA_FIELDS["SessionConfigCreate"]["prompt"]["description"],
        )
        yield field(
            SCHEMA_FIELDS["SessionConfigCreate"]["seed"]["title"],
            Input(self._initial_state.seed, type="integer", disabled=self._read_only, id="seed"),
            helper_text=SCHEMA_FIELDS["SessionConfigCreate"]["seed"]["description"],
        )
        yield field(
            SCHEMA_FIELDS["SessionConfigCreate"]["debate_round_count"]["title"],
            Input(
                self._initial_state.debate_round_count,
                type="integer",
                disabled=self._read_only,
                id="debate-round-count",
            ),
            helper_text=SCHEMA_FIELDS["SessionConfigCreate"]["debate_round_count"]["description"],
        )

    def form_state(self) -> GeneralFormState:
        return GeneralFormState(
            prompt=self.query_one("#prompt", TextArea).text,
            seed=self.query_one("#seed", Input).value,
            debate_round_count=self.query_one("#debate-round-count", Input).value,
        )
