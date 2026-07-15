from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input
from tui.screens.session_config.sections.debate.history.models import SlidingWindowHistoryFormState
from tui.widgets.forms.field import field


class SlidingWindowHistoryFields(Container):
    DEFAULT_CSS = """
    SlidingWindowHistoryFields {
        height: auto;
        width: 100%;
    }
    """

    can_focus = False

    def __init__(
        self,
        *,
        initial_state: SlidingWindowHistoryFormState,
        read_only: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            SCHEMA_FIELDS["SlidingWindowHistoryConfigCreate"]["window_size"]["title"],
            Input(
                self._initial_state.window_size,
                type="integer",
                disabled=self._read_only,
                id="history-window-size",
            ),
            helper_text=SCHEMA_FIELDS["SlidingWindowHistoryConfigCreate"]["window_size"]["description"],
        )

    def form_state(self) -> SlidingWindowHistoryFormState:
        return SlidingWindowHistoryFormState(window_size=self.query_one("#history-window-size", Input).value)
