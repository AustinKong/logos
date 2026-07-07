from uuid import uuid4

from api_client.models import ReasoningEffort
from attrs import define, field
from textual.widgets import Select

from tui.screens.session_config.sections.state import SelectValue


@define(frozen=True)
class ParticipantFormState:
    name: str
    model: SelectValue
    reasoning_effort: ReasoningEffort
    temperature: str
    system_prompt: str
    key: str = field(factory=lambda: uuid4().hex)


@define(frozen=True)
class ParticipantsFormState:
    participants: list[ParticipantFormState]


def participant_form_state(index: int, *, key: str | None = None) -> ParticipantFormState:
    return ParticipantFormState(
        name=f"Participant {index + 1}",
        model=Select.NULL,
        reasoning_effort=ReasoningEffort.NONE,
        temperature="0.7",
        system_prompt="",
        key=key or uuid4().hex,
    )
