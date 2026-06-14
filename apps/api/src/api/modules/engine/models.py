from dataclasses import dataclass

from api.modules.sessions.models.events import Event
from api.modules.sessions.models.participants import Participant
from api.modules.sessions.models.sessions import Session


@dataclass(slots=True)
class EngineContext:
    session: Session
    participants: list[Participant]
    events: list[Event]
