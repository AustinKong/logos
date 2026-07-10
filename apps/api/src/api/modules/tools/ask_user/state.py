from collections.abc import Iterable

from api.modules.sessions.models.events import Event
from api.modules.tools.ask_user.models import AskUserCompletedEvent, AskUserStartedEvent


# TODO: Pick a better file name for this.
def has_open_ask_user_calls(events: Iterable[Event]) -> bool:
    started_ids = {event.ask_user_id for event in events if isinstance(event, AskUserStartedEvent)}
    completed_ids = {event.ask_user_id for event in events if isinstance(event, AskUserCompletedEvent)}
    return bool(started_ids - completed_ids)
