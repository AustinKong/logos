from typing import assert_never

from api_client.models import (
    AgentParticipantCreate,
    AgentParticipantRead,
    ParticipantCreate,
    ParticipantRead,
    UserParticipantCreate,
    UserParticipantRead,
)
from textual.widgets import Select

from tui.screens.session_config.errors import SessionConfigValidationError
from tui.screens.session_config.sections.participants.state import (
    AgentParticipantFormState,
    ParticipantFormState,
    ParticipantsFormState,
    UserParticipantFormState,
)


def participants_form_state_from_read(participants: list[ParticipantRead]) -> ParticipantsFormState:
    return ParticipantsFormState(
        participants=[participant_form_state_from_read(participant) for participant in participants],
    )


def participants_create_from_form_state(state: ParticipantsFormState) -> list[ParticipantCreate]:
    return [participant_create_from_form_state(participant) for participant in state.participants]


def participant_form_state_from_read(participant: ParticipantRead) -> ParticipantFormState:
    match participant:
        case AgentParticipantRead():
            return AgentParticipantFormState(
                name=participant.name,
                model=participant.model,
                reasoning_effort=participant.reasoning_effort,
                system_prompt=participant.system_prompt,
            )
        case UserParticipantRead():
            return UserParticipantFormState(name=participant.name)
        case _ as never:
            assert_never(never)


def participant_create_from_form_state(participant: ParticipantFormState) -> ParticipantCreate:
    match participant:
        case AgentParticipantFormState():
            if not participant.name.strip():
                raise SessionConfigValidationError("Agent name is required")
            if participant.model == Select.NULL or not str(participant.model):
                raise SessionConfigValidationError("Agent model is required")
            model = str(participant.model)
            if not participant.system_prompt.strip():
                raise SessionConfigValidationError("Agent system prompt is required")

            return AgentParticipantCreate(
                name=participant.name,
                model=model,
                reasoning_effort=participant.reasoning_effort,
                system_prompt=participant.system_prompt,
            )
        case UserParticipantFormState():
            if not participant.name.strip():
                raise SessionConfigValidationError("User name is required")

            return UserParticipantCreate(name=participant.name)
        case _ as never:
            assert_never(never)
