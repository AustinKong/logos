from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from textual.widgets import Label, Select

from tui.shared.textual import on
from tui.widgets.forms.field import Field


@dataclass(frozen=True)
class SelectOption:
    label: str
    value: Any
    description: str | None = None


class SelectField(Field):
    def __init__(
        self,
        label: str,
        *,
        options: Sequence[SelectOption],
        value: Any = Select.NULL,
        allow_blank: bool = True,
        disabled: bool = False,
        select_id: str | None = None,
        select_classes: str | None = None,
    ) -> None:
        self._descriptions = {option.value: option.description or "" for option in options}
        super().__init__(
            Label(label, classes="label"),
            Select(
                [(option.label, option.value) for option in options],
                value=value,
                allow_blank=allow_blank,
                disabled=disabled,
                id=select_id,
                classes=select_classes,
            ),
            Label(self._descriptions.get(value, ""), classes="field-helper muted"),
        )

    @on(Select.Changed, stop=False)
    def handle_select_changed(self, event: Select.Changed) -> None:
        self.query_one(".field-helper", Label).update(self._descriptions.get(event.value, ""))
