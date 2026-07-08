from typing import assert_never

from api_client.models import (
    JudgeParticipantCreate,
    JudgeResolutionConfigCreate,
    JudgeResolutionConfigRead,
    NoneResolutionConfigCreate,
    NoneResolutionConfigRead,
)
from textual.widgets import Select

from tui.screens.session_config.errors import SessionConfigValidationError
from tui.screens.session_config.sections.participants.models import ParticipantFormState
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
                judge=ParticipantFormState(
                    name=resolution.judge.name,
                    model=resolution.judge.model,
                    reasoning_effort=resolution.judge.reasoning_effort,
                    verbosity=resolution.judge.verbosity,
                    temperature=str(resolution.judge.temperature),
                    system_prompt=resolution.judge.system_prompt,
                ),
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
            judge = resolution.judge
            if not judge.name.strip():
                raise SessionConfigValidationError("Judge name is required")
            if judge.model == Select.NULL or not str(judge.model):
                raise SessionConfigValidationError("Judge model is required")
            model = str(judge.model)
            if not judge.system_prompt.strip():
                raise SessionConfigValidationError("Judge system prompt is required")

            try:
                temperature = float(judge.temperature)
            except ValueError as exc:
                raise SessionConfigValidationError("Judge temperature must be a number") from exc

            return JudgeResolutionConfigCreate(
                judge=JudgeParticipantCreate(
                    name=judge.name,
                    model=model,
                    reasoning_effort=judge.reasoning_effort,
                    verbosity=judge.verbosity,
                    temperature=temperature,
                    system_prompt=judge.system_prompt,
                ),
            )
        case NoneResolutionFormState():
            return NoneResolutionConfigCreate()
        case _ as never:
            assert_never(never)
