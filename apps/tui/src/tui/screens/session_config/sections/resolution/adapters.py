from typing import assert_never

from api_client.models import (
    JudgeResolutionConfigCreate,
    JudgeResolutionConfigRead,
    JuryResolutionConfigCreate,
    JuryResolutionConfigRead,
    NoneResolutionConfigCreate,
    NoneResolutionConfigRead,
)

from tui.screens.participant_editor.adapters import participant_create_from_form_state
from tui.screens.participant_editor.models import ParticipantFormState
from tui.screens.session_config.sections.resolution.models import (
    JudgeResolutionFormState,
    JuryResolutionFormState,
    NoneResolutionFormState,
    ResolutionFormState,
)


def resolution_form_state_from_read(
    resolution: JudgeResolutionConfigRead | JuryResolutionConfigRead | NoneResolutionConfigRead,
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
        case JuryResolutionConfigRead():
            return JuryResolutionFormState(
                jurors=[
                    ParticipantFormState(
                        name=juror.name,
                        model=juror.model,
                        reasoning_effort=juror.reasoning_effort,
                        verbosity=juror.verbosity,
                        temperature=str(juror.temperature),
                        system_prompt=juror.system_prompt,
                    )
                    for juror in resolution.jurors
                ],
            )
        case NoneResolutionConfigRead():
            return NoneResolutionFormState()
        case _ as never:
            assert_never(never)


def resolution_create_from_form_state(
    resolution: ResolutionFormState,
) -> JudgeResolutionConfigCreate | JuryResolutionConfigCreate | NoneResolutionConfigCreate:
    match resolution:
        case JudgeResolutionFormState():
            judge = participant_create_from_form_state(
                resolution.judge,
                participant_label="Judge",
            )

            return JudgeResolutionConfigCreate(
                judge=judge,
            )
        case JuryResolutionFormState():
            return JuryResolutionConfigCreate(
                jurors=[
                    participant_create_from_form_state(juror, participant_label="Juror") for juror in resolution.jurors
                ],
            )
        case NoneResolutionFormState():
            return NoneResolutionConfigCreate()
        case _ as never:
            assert_never(never)
