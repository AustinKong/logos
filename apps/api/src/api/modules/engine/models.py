from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

from api.modules.sessions.models.events import Event
from api.modules.sessions.models.participants import Participant
from api.modules.sessions.models.sessions import Session


@dataclass(frozen=True, slots=True)
class Token:
    correlation_id: UUID
    content: str


type EngineOutput = Event | Token
type EngineOutputStream = AsyncIterator[EngineOutput]


@dataclass(slots=True)
class EngineContext:
    session: Session
    participants: list[Participant]
    events: list[Event]
