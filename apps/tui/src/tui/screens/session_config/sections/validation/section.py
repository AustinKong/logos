from typing import cast

from api_client.models import ValidationConfigRead, ValidationMode
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Select

from tui.screens.session_config.sections.validation.state import ValidationFormState
from tui.widgets.forms import field

VALIDATION_MODE_OPTIONS = [
    ("Allow all", ValidationMode.ALLOW_ALL),
]


class ValidationSection(VerticalScroll):
    can_focus = False

    def __init__(self, *, initial_state: ValidationFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            "Validation mode",
            Select(
                VALIDATION_MODE_OPTIONS,
                value=self._initial_state.mode,
                allow_blank=False,
                disabled=self._read_only,
            ),
        )

    def form_state(self) -> ValidationFormState:
        mode_select = self.query_one(Select)
        return ValidationConfigRead(mode=cast(ValidationMode, mode_select.value))
