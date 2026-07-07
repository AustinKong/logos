from typing import assert_never

from api_client.models import AIModelRead, ResolutionMode
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import ContentSwitcher, Select

from tui.screens.session_config.sections.resolution.models import (
    JudgeResolutionFormState,
    NoneResolutionFormState,
    ResolutionFormState,
    judge_participant_form_state,
)
from tui.screens.session_config.sections.resolution.modes.judge import JudgeResolutionFields
from tui.screens.session_config.sections.state import state_or_default
from tui.shared.textual import on
from tui.widgets.forms.select_field import SelectField, SelectOption

RESOLUTION_MODE_OPTIONS = [
    SelectOption(
        SCHEMA_FIELDS["JudgeResolutionConfigCreate"]["mode"]["title"],
        ResolutionMode.JUDGE_LLM,
        SCHEMA_FIELDS["JudgeResolutionConfigCreate"]["mode"]["description"],
    ),
    SelectOption(
        SCHEMA_FIELDS["NoneResolutionConfigCreate"]["mode"]["title"],
        ResolutionMode.NONE,
        SCHEMA_FIELDS["NoneResolutionConfigCreate"]["mode"]["description"],
    ),
]
RESOLUTION_MODE_CONTENT_IDS = {
    ResolutionMode.JUDGE_LLM: "judge-resolution-fields",
    ResolutionMode.NONE: "none-resolution-fields",
}


class ResolutionSection(VerticalScroll):
    DEFAULT_CSS = """
    ResolutionSection {
        height: auto;
        width: 100%;
    }
    """

    can_focus = False

    def __init__(
        self,
        *,
        initial_state: ResolutionFormState,
        models: list[AIModelRead],
        read_only: bool = False,
    ) -> None:
        super().__init__()
        self._initial_state = initial_state
        self._models = models
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield SelectField(
            "Resolution mode",
            options=RESOLUTION_MODE_OPTIONS,
            value=self._initial_state.mode,
            allow_blank=False,
            disabled=self._read_only,
            select_id="resolution-mode",
        )
        yield ContentSwitcher(
            Container(id=RESOLUTION_MODE_CONTENT_IDS[ResolutionMode.NONE]),
            JudgeResolutionFields(
                initial_state=state_or_default(
                    self._initial_state,
                    JudgeResolutionFormState,
                    JudgeResolutionFormState(judge=judge_participant_form_state()),
                ),
                models=self._models,
                read_only=self._read_only,
                id=RESOLUTION_MODE_CONTENT_IDS[ResolutionMode.JUDGE_LLM],
            ),
            initial=RESOLUTION_MODE_CONTENT_IDS[self._initial_state.mode],
            id="resolution-fields",
        )

    @on(Select.Changed, "#resolution-mode")
    def handle_resolution_mode_changed(self, event: Select.Changed) -> None:
        mode = ResolutionMode(event.value)
        switcher = self.query_one("#resolution-fields", ContentSwitcher)
        switcher.current = RESOLUTION_MODE_CONTENT_IDS[mode]

    def form_state(self) -> ResolutionFormState:
        mode_select = self.query_one("#resolution-mode", Select)
        match ResolutionMode(mode_select.value):
            case ResolutionMode.NONE:
                return NoneResolutionFormState()
            case ResolutionMode.JUDGE_LLM:
                return self.query_one(
                    f"#{RESOLUTION_MODE_CONTENT_IDS[ResolutionMode.JUDGE_LLM]}",
                    JudgeResolutionFields,
                ).form_state()
            case _ as never:
                assert_never(never)
