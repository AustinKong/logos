from typing import cast

from api_client.models import ContextConfigRead, ContextMode
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Select

from tui.screens.session_config.sections.context.state import ContextFormState
from tui.widgets.forms.select_field import SelectField, SelectOption

CONTEXT_MODE_OPTIONS = [
    SelectOption(
        SCHEMA_FIELDS["ContextConfigCreate"]["mode"]["title"],
        ContextMode.FULL,
        SCHEMA_FIELDS["ContextConfigCreate"]["mode"]["description"],
    ),
]


class ContextSection(VerticalScroll):
    can_focus = False

    def __init__(self, *, initial_state: ContextFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield SelectField(
            "Context mode",
            options=CONTEXT_MODE_OPTIONS,
            value=self._initial_state.mode,
            allow_blank=False,
            disabled=self._read_only,
            select_id="context-mode",
        )

    def form_state(self) -> ContextFormState:
        mode_select = self.query_one("#context-mode", Select)
        return ContextConfigRead(mode=cast(ContextMode, mode_select.value))
