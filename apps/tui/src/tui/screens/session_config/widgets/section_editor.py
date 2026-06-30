from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import TabbedContent, TabPane

from tui.screens.session_config.models import ConfigSection, ModelOptionState, SessionConfigFormState
from tui.screens.session_config.sections.context.section import ContextSection
from tui.screens.session_config.sections.participants.section import ParticipantsSection
from tui.screens.session_config.sections.prompt.section import PromptSection
from tui.screens.session_config.sections.resolution.section import ResolutionSection
from tui.screens.session_config.sections.turn_selection.section import TurnSelectionSection
from tui.screens.session_config.sections.validation.section import ValidationSection

SECTION_TAB_IDS = {
    ConfigSection.PROMPT: "prompt",
    ConfigSection.TURN_SELECTION: "turn-selection",
    ConfigSection.CONTEXT: "context",
    ConfigSection.VALIDATION: "validation",
    ConfigSection.RESOLUTION: "resolution",
    ConfigSection.PARTICIPANTS: "participants",
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
        model_options: list[ModelOptionState],
        read_only: bool = False,
    ) -> None:
        super().__init__(id="session-config")
        self._form_state = form_state
        self._model_options = model_options
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        with TabbedContent(initial=SECTION_TAB_IDS[ConfigSection.PROMPT], id="section-tabs"):
            yield TabPane(
                "Prompt",
                PromptSection(initial_state=self._form_state.prompt, read_only=self._read_only),
                id=SECTION_TAB_IDS[ConfigSection.PROMPT],
            )
            yield TabPane(
                "Turn Selection",
                TurnSelectionSection(initial_state=self._form_state.turn_selection, read_only=self._read_only),
                id=SECTION_TAB_IDS[ConfigSection.TURN_SELECTION],
            )
            yield TabPane(
                "Context",
                ContextSection(initial_state=self._form_state.context, read_only=self._read_only),
                id=SECTION_TAB_IDS[ConfigSection.CONTEXT],
            )
            yield TabPane(
                "Validation",
                ValidationSection(initial_state=self._form_state.validation, read_only=self._read_only),
                id=SECTION_TAB_IDS[ConfigSection.VALIDATION],
            )
            yield TabPane(
                "Resolution",
                ResolutionSection(
                    initial_state=self._form_state.resolution,
                    model_options=self._model_options,
                    read_only=self._read_only,
                ),
                id=SECTION_TAB_IDS[ConfigSection.RESOLUTION],
            )
            yield TabPane(
                "Participants",
                ParticipantsSection(
                    initial_state=self._form_state.participants,
                    model_options=self._model_options,
                    read_only=self._read_only,
                ),
                id=SECTION_TAB_IDS[ConfigSection.PARTICIPANTS],
            )

    def form_state(self) -> SessionConfigFormState:
        return SessionConfigFormState(
            prompt=self.query_one(PromptSection).form_state(),
            participants=self.query_one(ParticipantsSection).form_state(),
            turn_selection=self.query_one(TurnSelectionSection).form_state(),
            context=self.query_one(ContextSection).form_state(),
            validation=self.query_one(ValidationSection).form_state(),
            resolution=self.query_one(ResolutionSection).form_state(),
        )
