from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label

from tui.screens.session_config.sections.proposal.models import ProposalFormState


class ProposalSection(VerticalScroll):
    can_focus = False

    def __init__(self, *, initial_state: ProposalFormState, read_only: bool = False) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield Label("Proposal tool selection will be available here.", classes="muted")

    def form_state(self) -> ProposalFormState:
        return self._initial_state
