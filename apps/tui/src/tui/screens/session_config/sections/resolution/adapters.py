from typing import assert_never

from api_client.models import (
    JudgeResolutionConfigCreate,
    JudgeResolutionConfigRead,
    NoneResolutionConfigCreate,
    NoneResolutionConfigRead,
)
from textual.widgets import Select

from tui.screens.session_config.errors import SessionConfigValidationError
from tui.screens.session_config.sections.resolution.models import (
    JudgeResolutionFormState,
    NoneResolutionFormState,
    ResolutionFormState,
)


def resolution_form_state_from_read(
    resolution: JudgeResolutionConfigRead | NoneResolutionConfigRead,
) -> ResolutionFormState:
    match resolution:
        case JudgeResolutionConfigRead():
            return JudgeResolutionFormState(
                judge_model=resolution.judge_model,
                judge_temperature=str(resolution.judge_temperature),
            )
        case NoneResolutionConfigRead():
            return NoneResolutionFormState()
        case _ as never:
            assert_never(never)


def resolution_create_from_form_state(
    resolution: ResolutionFormState,
) -> JudgeResolutionConfigCreate | NoneResolutionConfigCreate:
    match resolution:
        case JudgeResolutionFormState():
            if resolution.judge_model == Select.NULL or not str(resolution.judge_model):
                raise SessionConfigValidationError("Judge model is required")
            judge_model = str(resolution.judge_model)

            try:
                judge_temperature = float(resolution.judge_temperature)
            except ValueError as exc:
                raise SessionConfigValidationError("Judge temperature must be a number") from exc

            return JudgeResolutionConfigCreate(
                judge_model=judge_model,
                judge_temperature=judge_temperature,
            )
        case NoneResolutionFormState():
            return NoneResolutionConfigCreate()
        case _ as never:
            assert_never(never)
