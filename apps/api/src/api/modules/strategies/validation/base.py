from typing import Protocol

from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import Event


class ValidationStrategy(Protocol):
    async def validate(self, ctx: EngineContext) -> list[Event]: ...
