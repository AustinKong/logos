from typing import Any

from api.modules.engine.models import Token
from api.modules.sessions.models.events import (
    Event,
    EventType,
    MessageCompletedEvent,
    MessageStartedEvent,
    ParticipantRemovedEvent,
    ParticipantVoteEvent,
    ResolutionCreatedEvent,
    SessionCompletedEvent,
    SessionStartedEvent,
)
from api.modules.sessions.models.participants import AgentParticipantConfig, Participant
from api.modules.sessions.models.sessions import Session
from api.modules.sessions.schemas import (
    AgentParticipantCreate,
    EventRead,
    MessageCompletedEventRead,
    MessageStartedEventRead,
    ParticipantRead,
    ParticipantRemovedEventRead,
    ParticipantVoteEventRead,
    ResolutionCreatedEventRead,
    SessionCompletedEventRead,
    SessionRead,
    SessionStartedEventRead,
    TokenRead,
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
        case MessageStartedEvent():
            return MessageStartedEventRead(
                **event_fields,
                type=EventType.MESSAGE_STARTED,
                message_id=event.message_id,
                sender=participant_read_from_participant(event.sender),
            )
        case MessageCompletedEvent():
            return MessageCompletedEventRead(
                **event_fields,
                type=EventType.MESSAGE_COMPLETED,
                message_id=event.message_id,
                content=event.content,
            )
        case ParticipantVoteEvent():
            return ParticipantVoteEventRead(
                **event_fields,
                type=EventType.PARTICIPANT_VOTE,
                voter=participant_read_from_participant(event.voter),
                target=participant_read_from_participant(event.target),
                reason=event.reason,
            )
        case ParticipantRemovedEvent():
            return ParticipantRemovedEventRead(
                **event_fields,
                type=EventType.PARTICIPANT_REMOVED,
                removed=participant_read_from_participant(event.removed),
            )
        case ResolutionCreatedEvent():
            return ResolutionCreatedEventRead(
                **event_fields,
                type=EventType.RESOLUTION_CREATED,
                resolution=event.resolution,
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


def token_read_from_token(token: Token) -> TokenRead:
    return TokenRead(correlation_id=token.correlation_id, content=token.content)
