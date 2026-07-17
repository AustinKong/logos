from api_client.models import AILanguageModelRead, ToolRead
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import TabbedContent, TabPane

from tui.screens.session_config.models import ConfigSection, SessionConfigFormState
from tui.screens.session_config.sections.debate.section import DebateSection
from tui.screens.session_config.sections.general.section import GeneralSection
from tui.screens.session_config.sections.proposal.section import ProposalSection
from tui.screens.session_config.sections.resolution.section import ResolutionSection

SECTION_TAB_IDS = {
    ConfigSection.GENERAL: "general",
    ConfigSection.PROPOSAL: "proposal",
    ConfigSection.DEBATE: "debate",
    ConfigSection.RESOLUTION: "resolution",
}


class SectionEditor(Container):
    DEFAULT_CSS = """
    SectionEditor {
        width: 100%;
        height: 100%;
    }

    SectionEditor #section-tabs {
        width: 100%;
        height: 100%;
    }

    SectionEditor #section-tabs > ContentSwitcher {
        width: 100%;
        height: 1fr;
    }

    SectionEditor TabPane {
        width: 100%;
        height: 100%;
    }
    """

    def __init__(
        self,
        *,
        form_state: SessionConfigFormState,
        models: list[AILanguageModelRead],
        proposal_tools: list[ToolRead],
        debate_tools: list[ToolRead],
        read_only: bool = False,
    ) -> None:
        super().__init__(id="session-config")
        self._form_state = form_state
        self._models = models
        self._proposal_tools = proposal_tools
        self._debate_tools = debate_tools
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        with TabbedContent(initial=SECTION_TAB_IDS[ConfigSection.GENERAL], id="section-tabs"):
            yield TabPane(
                "General",
                GeneralSection(initial_state=self._form_state.general, read_only=self._read_only),
                id=SECTION_TAB_IDS[ConfigSection.GENERAL],
            )
            yield TabPane(
                "Proposal",
                ProposalSection(
                    initial_state=self._form_state.proposal,
                    tools=self._proposal_tools,
                    read_only=self._read_only,
                ),
                id=SECTION_TAB_IDS[ConfigSection.PROPOSAL],
            )
            yield TabPane(
                "Debate",
                DebateSection(
                    initial_state=self._form_state.debate,
                    models=self._models,
                    tools=self._debate_tools,
                    read_only=self._read_only,
                ),
                id=SECTION_TAB_IDS[ConfigSection.DEBATE],
            )
            yield TabPane(
                "Resolution",
                ResolutionSection(
                    initial_state=self._form_state.resolution,
                    models=self._models,
                    read_only=self._read_only,
                ),
                id=SECTION_TAB_IDS[ConfigSection.RESOLUTION],
            )

    def form_state(self) -> SessionConfigFormState:
        return SessionConfigFormState(
            general=self.query_one(GeneralSection).form_state(),
            proposal=self.query_one(ProposalSection).form_state(),
            debate=self.query_one(DebateSection).form_state(),
            resolution=self.query_one(ResolutionSection).form_state(),
        )
