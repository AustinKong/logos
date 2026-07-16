from api.modules.session_configs.models.participants import (
    Participant,
    ParticipantData,
    ParticipantType,
)
from api.modules.session_configs.schemas.participants import (
    ParticipantCreate,
    ParticipantRead,
)


def participant_data_from_create(
    participant: ParticipantCreate,
    *,
    participant_type: ParticipantType,
) -> ParticipantData:
    return ParticipantData(
        name=participant.name,
        model=participant.model,
        system_prompt=participant.system_prompt,
        reasoning_effort=participant.reasoning_effort,
        verbosity=participant.verbosity,
        temperature=participant.temperature,
        type=participant_type,
    )


def participant_read_from_participant(participant: Participant) -> ParticipantRead:
    return ParticipantRead(
        id=participant.id,
        type=participant.type,
        name=participant.name,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
        model=participant.model,
        system_prompt=participant.system_prompt,
        reasoning_effort=participant.reasoning_effort,
        verbosity=participant.verbosity,
        temperature=participant.temperature,
    )
