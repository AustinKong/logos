from typing import Any

from api.modules.session_configs.adapters.participants import participant_read_from_participant
from api.modules.sessions.models.events import (
    AskUserCompletedEvent,
    AskUserStartedEvent,
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
    ResolutionVoteEvent,
    SessionCompletedEvent,
    SessionStartedEvent,
    TurnCompletedEvent,
    TurnStartedEvent,
)
from api.modules.sessions.schemas.events import (
    AskUserCompletedEventRead,
    AskUserStartedEventRead,
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
    ResolutionVoteEventRead,
    SessionCompletedEventRead,
    SessionStartedEventRead,
    TurnCompletedEventRead,
    TurnStartedEventRead,
)


def event_read_from_event(event: Event) -> EventRead:
    fields = _event_fields(event)

    match event:
        case TurnStartedEvent():
            return TurnStartedEventRead(
                **fields,
                type=EventType.TURN_STARTED,
                sender=participant_read_from_participant(event.sender),
            )
        case TurnCompletedEvent():
            return TurnCompletedEventRead(
                **fields,
                type=EventType.TURN_COMPLETED,
            )
        case AskUserStartedEvent():
            return AskUserStartedEventRead(
                **fields,
                type=EventType.ASK_USER_STARTED,
                question=event.question,
                options=event.options,
                requires_user_input=event.cache_entry_id is None,
            )
        case AskUserCompletedEvent():
            return ask_user_completed_event_read_from_event(event)
        case MessageStartedEvent():
            return MessageStartedEventRead(
                **fields,
                type=EventType.MESSAGE_STARTED,
            )
        case MessageCompletedEvent():
            return MessageCompletedEventRead(
                **fields,
                type=EventType.MESSAGE_COMPLETED,
                started_event_id=event.started_event_id,
                content=event.content,
            )
        case ReasoningStartedEvent():
            return ReasoningStartedEventRead(
                **fields,
                type=EventType.REASONING_STARTED,
            )
        case ReasoningCompletedEvent():
            return ReasoningCompletedEventRead(
                **fields,
                type=EventType.REASONING_COMPLETED,
                started_event_id=event.started_event_id,
                content=event.content,
            )
        case ProposalStartedEvent():
            return ProposalStartedEventRead(
                **fields,
                type=EventType.PROPOSAL_STARTED,
            )
        case ProposalCompletedEvent():
            return ProposalCompletedEventRead(
                **fields,
                type=EventType.PROPOSAL_COMPLETED,
            )
        case DebateRoundStartedEvent():
            return DebateRoundStartedEventRead(
                **fields,
                type=EventType.DEBATE_ROUND_STARTED,
                round_number=event.round_number,
            )
        case DebateRoundCompletedEvent():
            return DebateRoundCompletedEventRead(
                **fields,
                type=EventType.DEBATE_ROUND_COMPLETED,
            )
        case ResolutionStartedEvent():
            return ResolutionStartedEventRead(
                **fields,
                type=EventType.RESOLUTION_STARTED,
            )
        case ResolutionCompletedEvent():
            return ResolutionCompletedEventRead(
                **fields,
                type=EventType.RESOLUTION_COMPLETED,
                decision=event.decision,
            )
        case ResolutionVoteEvent():
            return ResolutionVoteEventRead(
                **fields,
                type=EventType.RESOLUTION_VOTE,
                selected_participant=participant_read_from_participant(event.selected_participant),
            )
        case SessionCompletedEvent():
            return SessionCompletedEventRead(
                **fields,
                type=EventType.SESSION_COMPLETED,
            )
        case SessionStartedEvent():
            return SessionStartedEventRead(
                **fields,
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


def ask_user_completed_event_read_from_event(event: AskUserCompletedEvent) -> AskUserCompletedEventRead:
    return AskUserCompletedEventRead(
        **_event_fields(event),
        type=EventType.ASK_USER_COMPLETED,
        started_event_id=event.started_event_id,
        answer_kind=event.answer_kind,
        answer=event.answer,
    )
