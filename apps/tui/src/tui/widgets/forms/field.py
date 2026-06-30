from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label


class Field(Vertical):
    DEFAULT_CSS = """
    Field {
        height: auto;
        width: 100%;
        margin-bottom: 1;
    }

    Field .field-label {
        height: auto;
        width: 100%;
        color: $text-secondary;
    }

    Field .field-helper {
        height: auto;
        width: 100%;
        color: $text-muted;
    }
    """


def field(
    label: str,
    widget: Widget,
    *,
    helper_text: str | None = None,
    helper_id: str | None = None,
) -> Field:
    children: list[Widget] = [
        Label(label, classes="field-label"),
        widget,
    ]
    if helper_text:
        children.append(Label(helper_text, id=helper_id, classes="field-helper"))

    return Field(
        *children,
    )
