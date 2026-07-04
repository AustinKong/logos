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
    """


def field(
    label: str,
    widget: Widget,
    *,
    helper_text: str | None = None,
    helper_id: str | None = None,
) -> Field:
    children: list[Widget] = [
        Label(label, classes="label"),
        widget,
    ]
    if helper_text:
        children.append(Label(helper_text, id=helper_id, classes="muted"))

    return Field(
        *children,
    )
