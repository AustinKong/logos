from api_client.models import (
    JudgeResolutionConfigCreate,
    JudgeResolutionConfigRead,
    NoneResolutionConfigCreate,
    NoneResolutionConfigRead,
)
from textual.widgets import Select

from tui.screens.session_config.errors import SessionConfigValidationError
from tui.screens.session_config.sections.resolution.state import (
    JudgeResolutionFormState,
    NoneResolutionFormState,
    ResolutionFormState,
)


def resolution_form_state_from_read(
    resolution: JudgeResolutionConfigRead | NoneResolutionConfigRead,
) -> ResolutionFormState:
    if isinstance(resolution, JudgeResolutionConfigRead):
        return JudgeResolutionFormState(
            judge_model=resolution.judge_model,
            judge_temperature=str(resolution.judge_temperature),
        )

    return NoneResolutionFormState()


def resolution_create_from_form_state(
    resolution: ResolutionFormState,
) -> JudgeResolutionConfigCreate | NoneResolutionConfigCreate:
    if isinstance(resolution, JudgeResolutionFormState):
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

    return NoneResolutionConfigCreate()
