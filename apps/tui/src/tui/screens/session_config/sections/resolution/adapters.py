from typing import assert_never

from api_client.models import (
    JudgeResolutionConfigCreate,
    JudgeResolutionConfigRead,
    NoneResolutionConfigCreate,
    NoneResolutionConfigRead,
)

from tui.screens.participant_editor.adapters import participant_create_from_form_state
from tui.screens.participant_editor.models import ParticipantFormState
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
            judge = participant_create_from_form_state(
                resolution.judge,
                participant_label="Judge",
            )

            return JudgeResolutionConfigCreate(
                judge=judge,
            )
        case NoneResolutionFormState():
            return NoneResolutionConfigCreate()
        case _ as never:
            assert_never(never)
