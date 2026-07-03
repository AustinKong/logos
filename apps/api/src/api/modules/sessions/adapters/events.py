from typing import Any

from api.modules.session_configs.adapters.participants import participant_read_from_participant
from api.modules.sessions.models.events import (
    Event,
    EventType,
    MessageCompletedEvent,
    MessageStartedEvent,
    ParticipantRemovedEvent,
    ParticipantVoteEvent,
    ReasoningCompletedEvent,
    ReasoningStartedEvent,
    ResolutionCreatedEvent,
    SessionCompletedEvent,
    SessionStartedEvent,
)
from api.modules.sessions.schemas.events import (
    EventRead,
    MessageCompletedEventRead,
    MessageStartedEventRead,
    ParticipantRemovedEventRead,
    ParticipantVoteEventRead,
    ReasoningCompletedEventRead,
    ReasoningStartedEventRead,
    ResolutionCreatedEventRead,
    SessionCompletedEventRead,
    SessionStartedEventRead,
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
        case ReasoningStartedEvent():
            return ReasoningStartedEventRead(
                **event_fields,
                type=EventType.REASONING_STARTED,
                reasoning_id=event.reasoning_id,
                sender=participant_read_from_participant(event.sender),
            )
        case ReasoningCompletedEvent():
            return ReasoningCompletedEventRead(
                **event_fields,
                type=EventType.REASONING_COMPLETED,
                reasoning_id=event.reasoning_id,
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
