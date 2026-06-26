from api.modules.session_configs.errors import UnsupportedParticipantCreateError
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
            )
        case UserParticipantCreate():
            return UserParticipantData()

    raise UnsupportedParticipantCreateError()


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
            )
        case UserParticipant():
            return UserParticipantRead(
                id=participant.id,
                created_at=participant.created_at,
                updated_at=participant.updated_at,
            )

    raise ValueError(f"Unsupported participant type: {participant.type}")
