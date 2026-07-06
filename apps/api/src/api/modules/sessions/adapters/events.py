from typing import Any

from api.modules.session_configs.adapters.participants import participant_read_from_participant
from api.modules.sessions.models.events import (
    DebateRoundCompletedEvent,
    DebateRoundStartedEvent,
    Event,
    EventType,
    MessageCompletedEvent,
    MessageStartedEvent,
    ProposalCompletedEvent,
    ProposalStartedEvent,
    ReasoningCompletedEvent,
    ReasoningStartedEvent,
    ResolutionCompletedEvent,
    ResolutionStartedEvent,
    SessionCompletedEvent,
    SessionStartedEvent,
)
from api.modules.sessions.schemas.events import (
    DebateRoundCompletedEventRead,
    DebateRoundStartedEventRead,
    EventRead,
    MessageCompletedEventRead,
    MessageStartedEventRead,
    ProposalCompletedEventRead,
    ProposalStartedEventRead,
    ReasoningCompletedEventRead,
    ReasoningStartedEventRead,
    ResolutionCompletedEventRead,
    ResolutionStartedEventRead,
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
        case ProposalStartedEvent():
            return ProposalStartedEventRead(
                **event_fields,
                type=EventType.PROPOSAL_STARTED,
            )
        case ProposalCompletedEvent():
            return ProposalCompletedEventRead(
                **event_fields,
                type=EventType.PROPOSAL_COMPLETED,
            )
        case DebateRoundStartedEvent():
            return DebateRoundStartedEventRead(
                **event_fields,
                type=EventType.DEBATE_ROUND_STARTED,
                round_number=event.round_number,
            )
        case DebateRoundCompletedEvent():
            return DebateRoundCompletedEventRead(
                **event_fields,
                type=EventType.DEBATE_ROUND_COMPLETED,
            )
        case ResolutionStartedEvent():
            return ResolutionStartedEventRead(
                **event_fields,
                type=EventType.RESOLUTION_STARTED,
            )
        case ResolutionCompletedEvent():
            return ResolutionCompletedEventRead(
                **event_fields,
                type=EventType.RESOLUTION_COMPLETED,
                decision=event.decision,
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
