from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import Event, MessageCompletedEvent, MessageStartedEvent

# TODO: More sophisticated transcript formatting in future, e.g. other event types


@dataclass(frozen=True, slots=True)
class MessageEventPair:
    started: MessageStartedEvent
    completed: MessageCompletedEvent


def format_message_transcript(ctx: EngineContext, *, empty_text: str | None = None) -> str | None:
    participant_names = {participant.id: participant.name for participant in ctx.participants}
    lines = [
        f"{participant_names.get(message.started.sender_id, 'Unknown participant')}: {message.completed.content}"
        for message in iter_message_event_pairs(ctx.events)
    ]
    if not lines:
        return empty_text

    return "\n".join(lines)


# TODO: Move to a separate file, and make this more generic for other types of paired events
def iter_message_event_pairs(events: Iterable[Event]) -> Iterator[MessageEventPair]:
    events = tuple(events)
    message_started_by_id = {event.message_id: event for event in events if isinstance(event, MessageStartedEvent)}
    return (
        MessageEventPair(started=message_started, completed=event)
        for event in events
        if isinstance(event, MessageCompletedEvent)
        if (message_started := message_started_by_id.get(event.message_id)) is not None
    )
