from typing import Protocol

from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import Event


class ResolutionStrategy(Protocol):
    async def resolve(self, ctx: EngineContext) -> list[Event]: ...
