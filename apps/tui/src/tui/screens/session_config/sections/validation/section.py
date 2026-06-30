from typing import cast

from api_client.models import ValidationConfigRead, ValidationMode
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Select

from tui.screens.session_config.sections.validation.state import ValidationFormState
from tui.widgets.forms.select_field import SelectField, SelectOption

VALIDATION_MODE_OPTIONS = [
    SelectOption(
        SCHEMA_FIELDS["ValidationConfigCreate"]["mode"]["title"],
        ValidationMode.ALLOW_ALL,
        SCHEMA_FIELDS["ValidationConfigCreate"]["mode"]["description"],
    ),
]


class ValidationSection(VerticalScroll):
    can_focus = False

    def __init__(self, *, initial_state: ValidationFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield SelectField(
            "Validation mode",
            options=VALIDATION_MODE_OPTIONS,
            value=self._initial_state.mode,
            allow_blank=False,
            disabled=self._read_only,
        )

    def form_state(self) -> ValidationFormState:
        mode_select = self.query_one(Select)
        return ValidationConfigRead(mode=cast(ValidationMode, mode_select.value))
