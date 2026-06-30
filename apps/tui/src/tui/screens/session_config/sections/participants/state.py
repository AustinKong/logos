from uuid import uuid4

from api_client.models import ParticipantType
from attrs import define, field
from textual.widgets import Select

from tui.screens.session_config.sections.state import SelectValue


@define(frozen=True)
class AgentParticipantFormState:
    name: str
    model: SelectValue
    system_prompt: str
    key: str = field(factory=lambda: uuid4().hex)
    type_: ParticipantType = ParticipantType.AGENT


@define(frozen=True)
class UserParticipantFormState:
    name: str
    key: str = field(factory=lambda: uuid4().hex)
    type_: ParticipantType = ParticipantType.USER


type ParticipantFormState = AgentParticipantFormState | UserParticipantFormState


@define(frozen=True)
class ParticipantsFormState:
    participants: list[ParticipantFormState]


def agent_participant_form_state(index: int, *, key: str | None = None) -> AgentParticipantFormState:
    return AgentParticipantFormState(
        name=f"Agent {index + 1}",
        model=Select.NULL,
        system_prompt="",
        key=key or uuid4().hex,
    )


def user_participant_form_state(index: int, *, key: str) -> UserParticipantFormState:
    return UserParticipantFormState(
        name=f"User {index + 1}",
        key=key,
    )
