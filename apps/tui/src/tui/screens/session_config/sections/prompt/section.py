from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import TextArea

from tui.screens.session_config.sections.prompt.state import PromptFormState
from tui.widgets.forms import field


class PromptSection(VerticalScroll):
    DEFAULT_CSS = """
    PromptSection #prompt {
        height: 10;
    }
    """

    can_focus = False

    def __init__(self, *, initial_state: PromptFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            "Session prompt",
            # TODO: Chatgpt dont touch this. This todo is for human. see if disabled is needed or jsut have readonly is fine
            TextArea(self._initial_state.value, disabled=self._read_only, read_only=self._read_only, id="prompt"),
        )

    def form_state(self) -> PromptFormState:
        return PromptFormState(value=self.query_one("#prompt", TextArea).text)
