from api_client.models import ResolutionMode
from attrs import define

from tui.screens.session_config.sections.state import SelectValue


@define(frozen=True)
class JudgeResolutionFormState:
    judge_model: SelectValue
    judge_temperature: str
    mode: ResolutionMode = ResolutionMode.JUDGE_LLM


@define(frozen=True)
class NoneResolutionFormState:
    mode: ResolutionMode = ResolutionMode.NONE


type ResolutionFormState = JudgeResolutionFormState | NoneResolutionFormState
