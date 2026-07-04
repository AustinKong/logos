from typing import assert_never

from api.modules.session_configs.models.participants import (
    AgentParticipant,
    AgentParticipantData,
    Participant,
    ParticipantData,
    UserParticipant,
    UserParticipantData,
)
from api.modules.session_configs.schemas.participants import (
    AgentParticipantCreate,
    AgentParticipantRead,
    ParticipantCreate,
    ParticipantRead,
    UserParticipantCreate,
    UserParticipantRead,
)


def participant_data_from_create(participant: ParticipantCreate) -> ParticipantData:
    match participant:
        case AgentParticipantCreate():
            return AgentParticipantData(
                name=participant.name,
                model=participant.model,
                system_prompt=participant.system_prompt,
                reasoning_effort=participant.reasoning_effort,
            )
        case UserParticipantCreate():
            return UserParticipantData(name=participant.name)
        case _ as never:
            assert_never(never)


def participant_read_from_participant(participant: Participant) -> ParticipantRead:
    match participant:
        case AgentParticipant():
            return AgentParticipantRead(
                id=participant.id,
                name=participant.name,
                created_at=participant.created_at,
                updated_at=participant.updated_at,
                model=participant.model,
                system_prompt=participant.system_prompt,
                reasoning_effort=participant.reasoning_effort,
            )
        case UserParticipant():
            return UserParticipantRead(
                id=participant.id,
                name=participant.name,
                created_at=participant.created_at,
                updated_at=participant.updated_at,
            )
        case _:
            raise ValueError(f"Unsupported participant type: {participant.type}")
