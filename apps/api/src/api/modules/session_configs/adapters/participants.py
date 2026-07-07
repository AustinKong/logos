from api.modules.session_configs.models.participants import (
    DebaterParticipant,
    JudgeParticipant,
    JurorParticipant,
    Participant,
    ParticipantData,
    ParticipantType,
)
from api.modules.session_configs.schemas.participants import (
    DebaterParticipantCreate,
    DebaterParticipantRead,
    JudgeParticipantCreate,
    JudgeParticipantRead,
    JurorParticipantRead,
    ParticipantRead,
)


def debater_participant_data_from_create(participant: DebaterParticipantCreate) -> ParticipantData:
    return _participant_data_from_create(participant, participant_type=ParticipantType.DEBATER)


def judge_participant_data_from_create(participant: JudgeParticipantCreate) -> ParticipantData:
    return _participant_data_from_create(participant, participant_type=ParticipantType.JUDGE)


def _participant_data_from_create(
    participant: DebaterParticipantCreate | JudgeParticipantCreate,
    *,
    participant_type: ParticipantType,
) -> ParticipantData:
    return ParticipantData(
        name=participant.name,
        model=participant.model,
        system_prompt=participant.system_prompt,
        reasoning_effort=participant.reasoning_effort,
        temperature=participant.temperature,
        type=participant_type,
    )


def participant_read_from_participant(participant: Participant) -> ParticipantRead:
    match participant:
        case DebaterParticipant():
            return debater_participant_read_from_participant(participant)
        case JudgeParticipant():
            return judge_participant_read_from_participant(participant)
        case JurorParticipant():
            return juror_participant_read_from_participant(participant)
        case _:
            raise ValueError(f"Unsupported participant type: {participant.type}")


def debater_participant_read_from_participant(participant: DebaterParticipant) -> DebaterParticipantRead:
    return DebaterParticipantRead(
        id=participant.id,
        type=ParticipantType.DEBATER,
        name=participant.name,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
        model=participant.model,
        system_prompt=participant.system_prompt,
        reasoning_effort=participant.reasoning_effort,
        temperature=participant.temperature,
    )


def judge_participant_read_from_participant(participant: JudgeParticipant) -> JudgeParticipantRead:
    return JudgeParticipantRead(
        id=participant.id,
        type=ParticipantType.JUDGE,
        name=participant.name,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
        model=participant.model,
        system_prompt=participant.system_prompt,
        reasoning_effort=participant.reasoning_effort,
        temperature=participant.temperature,
    )


def juror_participant_read_from_participant(participant: JurorParticipant) -> JurorParticipantRead:
    return JurorParticipantRead(
        id=participant.id,
        type=ParticipantType.JUROR,
        name=participant.name,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
        model=participant.model,
        system_prompt=participant.system_prompt,
        reasoning_effort=participant.reasoning_effort,
        temperature=participant.temperature,
    )
