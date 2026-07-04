from typing import assert_never

from api_client.models import HistoryMode
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import ContentSwitcher, Select

from tui.screens.session_config.sections.history.models import (
    FullHistoryFormState,
    HistoryFormState,
    SlidingWindowHistoryFormState,
)
from tui.screens.session_config.sections.history.modes.sliding_window import SlidingWindowHistoryFields
from tui.screens.session_config.sections.state import state_or_default
from tui.shared.textual import on
from tui.widgets.forms.select_field import SelectField, SelectOption

HISTORY_MODE_OPTIONS = [
    SelectOption(
        SCHEMA_FIELDS["FullHistoryConfigCreate"]["mode"]["title"],
        HistoryMode.FULL,
        SCHEMA_FIELDS["FullHistoryConfigCreate"]["mode"]["description"],
    ),
    SelectOption(
        SCHEMA_FIELDS["SlidingWindowHistoryConfigCreate"]["mode"]["title"],
        HistoryMode.SLIDING_WINDOW,
        SCHEMA_FIELDS["SlidingWindowHistoryConfigCreate"]["mode"]["description"],
    ),
]
HISTORY_MODE_CONTENT_IDS = {
    HistoryMode.FULL: "full-history-fields",
    HistoryMode.SLIDING_WINDOW: "sliding-window-history-fields",
}


class HistorySection(VerticalScroll):
    can_focus = False

    def __init__(self, *, initial_state: HistoryFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield SelectField(
            "History mode",
            options=HISTORY_MODE_OPTIONS,
            value=self._initial_state.mode,
            allow_blank=False,
            disabled=self._read_only,
            select_id="history-mode",
        )
        yield ContentSwitcher(
            Container(id=HISTORY_MODE_CONTENT_IDS[HistoryMode.FULL]),
            SlidingWindowHistoryFields(
                initial_state=state_or_default(
                    self._initial_state,
                    SlidingWindowHistoryFormState,
                    SlidingWindowHistoryFormState(window_size="5"),
                ),
                read_only=self._read_only,
                id=HISTORY_MODE_CONTENT_IDS[HistoryMode.SLIDING_WINDOW],
            ),
            initial=HISTORY_MODE_CONTENT_IDS[self._initial_state.mode],
            id="history-fields",
        )

    @on(Select.Changed, "#history-mode")
    def handle_history_mode_changed(self, event: Select.Changed) -> None:
        mode = HistoryMode(event.value)
        switcher = self.query_one("#history-fields", ContentSwitcher)
        switcher.current = HISTORY_MODE_CONTENT_IDS[mode]

    def form_state(self) -> HistoryFormState:
        mode_select = self.query_one("#history-mode", Select)
        match HistoryMode(mode_select.value):
            case HistoryMode.FULL:
                return FullHistoryFormState()
            case HistoryMode.SLIDING_WINDOW:
                return self.query_one(
                    f"#{HISTORY_MODE_CONTENT_IDS[HistoryMode.SLIDING_WINDOW]}",
                    SlidingWindowHistoryFields,
                ).form_state()
            case _ as never:
                assert_never(never)
