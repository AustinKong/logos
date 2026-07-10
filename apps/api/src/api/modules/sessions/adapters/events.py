from api.modules.session_configs.adapters.participants import participant_read_from_participant
from api.modules.sessions.adapters.base import event_fields
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
from api.modules.tools.ask_user.adapters import (
    ask_user_completed_event_read_from_event,
    ask_user_started_event_read_from_event,
)
from api.modules.tools.ask_user.models import AskUserCompletedEvent, AskUserStartedEvent


def event_read_from_event(event: Event) -> EventRead:
    fields = event_fields(event)

    match event:
        case AskUserStartedEvent():
            return ask_user_started_event_read_from_event(event)
        case AskUserCompletedEvent():
            return ask_user_completed_event_read_from_event(event)
        case MessageStartedEvent():
            return MessageStartedEventRead(
                **fields,
                type=EventType.MESSAGE_STARTED,
                message_id=event.message_id,
                sender=participant_read_from_participant(event.sender),
            )
        case MessageCompletedEvent():
            return MessageCompletedEventRead(
                **fields,
                type=EventType.MESSAGE_COMPLETED,
                message_id=event.message_id,
                content=event.content,
            )
        case ReasoningStartedEvent():
            return ReasoningStartedEventRead(
                **fields,
                type=EventType.REASONING_STARTED,
                reasoning_id=event.reasoning_id,
                sender=participant_read_from_participant(event.sender),
            )
        case ReasoningCompletedEvent():
            return ReasoningCompletedEventRead(
                **fields,
                type=EventType.REASONING_COMPLETED,
                reasoning_id=event.reasoning_id,
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
