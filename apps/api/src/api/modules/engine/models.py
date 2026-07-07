from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

from api.modules.session_configs.models.participants import DebaterParticipant
from api.modules.sessions.models.events import Event


@dataclass(frozen=True, slots=True)
class Token:
    correlation_id: UUID
    content: str


type EngineOutput = Event | Token
type EngineOutputStream = AsyncIterator[EngineOutput]


# Does not hold `session: Session` to avoid runtime dependencies on session config
# Instead configs should be passed explicitly via strategy constructors
# Prompt and seed are included since they are broadly shared across strategies.
@dataclass(slots=True)
class EngineContext:
    session_id: UUID
    prompt: str
    seed: int
    debaters: list[DebaterParticipant]
    events: list[Event]
