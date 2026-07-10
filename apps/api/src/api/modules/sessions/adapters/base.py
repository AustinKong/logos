from typing import Any

from api.modules.sessions.models.events import Event


# TODO: Weird that this is in base.py
def event_fields(event: Event) -> dict[str, Any]:
    return {
        "id": event.id,
        "session_id": event.session_id,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
    }
