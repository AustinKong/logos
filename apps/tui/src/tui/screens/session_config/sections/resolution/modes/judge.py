from typing import cast

from api_client.models import AIModelRead
from api_client.schema_metadata import SCHEMA_FIELDS
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input, Select

from tui.screens.session_config.sections.resolution.models import JudgeResolutionFormState
from tui.screens.session_config.sections.state import SelectValue
from tui.widgets.forms.field import field


class JudgeResolutionFields(Container):
    DEFAULT_CSS = """
    JudgeResolutionFields {
        height: auto;
        width: 100%;
    }
    """

    can_focus = False

    def __init__(
        self,
        *,
        initial_state: JudgeResolutionFormState,
        models: list[AIModelRead],
        read_only: bool = False,
        id: str | None = None,
    ) -> None:
        super().__init__(id=id)
        self._initial_state = initial_state
        self._models = models
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield field(
            SCHEMA_FIELDS["JudgeResolutionConfigCreate"]["judge_model"]["title"],
            Select(
                [(model.label, model.id) for model in self._models],
                value=self._initial_state.judge_model,
                allow_blank=True,
                disabled=self._read_only,
                id="judge-model",
            ),
            helper_text=SCHEMA_FIELDS["JudgeResolutionConfigCreate"]["judge_model"]["description"],
        )
        yield field(
            SCHEMA_FIELDS["JudgeResolutionConfigCreate"]["judge_temperature"]["title"],
            Input(
                self._initial_state.judge_temperature,
                type="number",
                disabled=self._read_only,
                id="judge-temperature",
            ),
            helper_text=SCHEMA_FIELDS["JudgeResolutionConfigCreate"]["judge_temperature"]["description"],
        )

    def form_state(self) -> JudgeResolutionFormState:
        model_select = self.query_one("#judge-model", Select)
        judge_temperature = self.query_one("#judge-temperature", Input).value
        return JudgeResolutionFormState(
            judge_model=cast(SelectValue, model_select.value),
            judge_temperature=judge_temperature,
        )
