from api_client.models import ToolRead
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import VerticalScroll

from tui.screens.session_config.sections.proposal.models import ProposalFormState
from tui.widgets.forms.field import field
from tui.widgets.tools_select import ToolsSelect


class ProposalSection(VerticalScroll):
    can_focus = False

    def __init__(
        self,
        *,
        initial_state: ProposalFormState,
        tools: list[ToolRead],
        read_only: bool = False,
    ) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._tools = tools
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            SCHEMA_FIELDS["ProposalConfigCreate"]["tools"]["title"],
            ToolsSelect(
                tools=self._tools,
                initial_values=self._initial_state.tools,
                read_only=self._read_only,
            ),
            helper_text=SCHEMA_FIELDS["ProposalConfigCreate"]["tools"]["description"],
        )

    def form_state(self) -> ProposalFormState:
        return ProposalFormState(tools=self.query_one(ToolsSelect).form_state())
