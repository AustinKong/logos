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
    """


def field(label: str, widget: Widget) -> Field:
    return Field(
        Label(label, classes="field-label"),
        widget,
    )
