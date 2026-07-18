from api_client.models import ReasoningEffort, ResolutionMode, Verbosity
from attrs import define
from textual.widgets import Select

from tui.screens.participant_editor.models import ParticipantFormState


@define(frozen=True)
class JudgeResolutionFormState:
    judge: ParticipantFormState
    mode: ResolutionMode = ResolutionMode.JUDGE


@define(frozen=True)
class JuryResolutionFormState:
    jurors: list[ParticipantFormState]
    mode: ResolutionMode = ResolutionMode.JURY


@define(frozen=True)
class NoneResolutionFormState:
    mode: ResolutionMode = ResolutionMode.NONE


type ResolutionFormState = JudgeResolutionFormState | JuryResolutionFormState | NoneResolutionFormState


def judge_participant_form_state() -> ParticipantFormState:
    return ParticipantFormState(
        name="Judge",
        model=Select.NULL,
        reasoning_effort=ReasoningEffort.NONE,
        verbosity=Verbosity.MEDIUM,
        temperature="0.2",
        system_prompt="Resolve the debate neutrally using only the transcript.",
    )


# TODO: Centralize these defaults in shared client.
def juror_participant_form_state(number: int) -> ParticipantFormState:
    return ParticipantFormState(
        name=f"Juror {number}",
        model=Select.NULL,
        reasoning_effort=ReasoningEffort.NONE,
        verbosity=Verbosity.MEDIUM,
        temperature="0.2",
        system_prompt="Review the debate independently and vote for the strongest position.",
    )
