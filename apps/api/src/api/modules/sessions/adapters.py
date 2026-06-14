from typing import Any

from api.modules.sessions.models.events import (
    Event,
    EventType,
    ParticipantMessageEvent,
    ParticipantRemovedEvent,
    ParticipantVoteEvent,
    SessionCompletedEvent,
    SessionStartedEvent,
)
from api.modules.sessions.models.participants import AgentParticipantConfig, Participant
from api.modules.sessions.models.sessions import Session
from api.modules.sessions.schemas import (
    AgentParticipantCreate,
    EventRead,
    ParticipantMessageEventRead,
    ParticipantRead,
    ParticipantRemovedEventRead,
    ParticipantVoteEventRead,
    SessionCompletedEventRead,
    SessionRead,
    SessionStartedEventRead,
)


def agent_participant_config_from_create(agent: AgentParticipantCreate) -> AgentParticipantConfig:
    return AgentParticipantConfig(
        name=agent.name,
        model=agent.model,
        system_prompt=agent.system_prompt,
    )


def participant_read_from_participant(participant: Participant) -> ParticipantRead:
    return ParticipantRead(
        id=participant.id,
        type=participant.type,
        name=participant.name,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
    )


def session_read_from_session(session: Session) -> SessionRead:
    return SessionRead(
        id=session.id,
        prompt=session.prompt,
        created_at=session.created_at,
        updated_at=session.updated_at,
        participants=[participant_read_from_participant(participant) for participant in session.participants],
    )


def event_read_from_event(event: Event) -> EventRead:
    event_fields = _event_fields(event)

    match event:
        case ParticipantMessageEvent():
            return ParticipantMessageEventRead(
                **event_fields,
                type=EventType.PARTICIPANT_MESSAGE,
                sender_id=event.sender_id,
                content=event.content,
            )
        case ParticipantVoteEvent():
            return ParticipantVoteEventRead(
                **event_fields,
                type=EventType.PARTICIPANT_VOTE,
                voter_id=event.voter_id,
                target_id=event.target_id,
                reason=event.reason,
            )
        case ParticipantRemovedEvent():
            return ParticipantRemovedEventRead(
                **event_fields,
                type=EventType.PARTICIPANT_REMOVED,
                removed_id=event.removed_id,
            )
        case SessionCompletedEvent():
            return SessionCompletedEventRead(
                **event_fields,
                type=EventType.SESSION_COMPLETED,
            )
        case SessionStartedEvent():
            return SessionStartedEventRead(
                **event_fields,
                type=EventType.SESSION_STARTED,
            )

    raise ValueError(f"Unsupported event type: {event.type}")


def _event_fields(event: Event) -> dict[str, Any]:
    return {
        "id": event.id,
        "session_id": event.session_id,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
    }
