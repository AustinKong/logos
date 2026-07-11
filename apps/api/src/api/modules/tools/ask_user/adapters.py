from api.modules.sessions.adapters.base import event_fields
from api.modules.sessions.models.events import EventType
from api.modules.tools.ask_user.models import AskUserCompletedEvent, AskUserStartedEvent
from api.modules.tools.ask_user.schemas import AskUserCompletedEventRead, AskUserStartedEventRead


def ask_user_started_event_read_from_event(event: AskUserStartedEvent) -> AskUserStartedEventRead:
    return AskUserStartedEventRead(
        **event_fields(event),
        type=EventType.ASK_USER_STARTED,
        ask_user_id=event.ask_user_id,
        question=event.question,
        options=event.options,
        requires_user_input=event.cache_entry_id is None,
    )


def ask_user_completed_event_read_from_event(event: AskUserCompletedEvent) -> AskUserCompletedEventRead:
    return AskUserCompletedEventRead(
        **event_fields(event),
        type=EventType.ASK_USER_COMPLETED,
        ask_user_id=event.ask_user_id,
        answer_kind=event.answer_kind,
        answer=event.answer,
    )
