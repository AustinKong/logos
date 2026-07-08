from api_client.models import ReasoningEffort, ResolutionMode, Verbosity
from attrs import define
from textual.widgets import Select

from tui.screens.session_config.sections.participants.models import ParticipantFormState


@define(frozen=True)
class JudgeResolutionFormState:
    judge: ParticipantFormState
    mode: ResolutionMode = ResolutionMode.JUDGE_LLM


@define(frozen=True)
class NoneResolutionFormState:
    mode: ResolutionMode = ResolutionMode.NONE


type ResolutionFormState = JudgeResolutionFormState | NoneResolutionFormState


def judge_participant_form_state() -> ParticipantFormState:
    return ParticipantFormState(
        name="Judge",
        model=Select.NULL,
        reasoning_effort=ReasoningEffort.NONE,
        verbosity=Verbosity.MEDIUM,
        temperature="0.2",
        system_prompt="Resolve the debate neutrally using only the transcript.",
    )
