from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import Event, MessageCompletedEvent, MessageStartedEvent


@dataclass(frozen=True, slots=True)
class MessageEventPair:
    started: MessageStartedEvent
    completed: MessageCompletedEvent


def format_message_transcript(
    ctx: EngineContext,
    *,
    limit: int | None = None,
) -> str | None:
    messages = tuple(iter_message_event_pairs(ctx.events))
    if limit is not None:
        messages = messages[-limit:]

    lines = [f"{message.started.sender.name}: {message.completed.content}" for message in messages]
    if not lines:
        return None

    return "\n".join(lines)


def iter_message_event_pairs(events: Iterable[Event]) -> Iterator[MessageEventPair]:
    events = tuple(events)
    message_started_by_id = {event.message_id: event for event in events if isinstance(event, MessageStartedEvent)}
    return (
        MessageEventPair(started=message_started, completed=event)
        for event in events
        if isinstance(event, MessageCompletedEvent)
        if (message_started := message_started_by_id.get(event.message_id)) is not None
    )
