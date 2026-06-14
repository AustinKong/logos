from typing import Protocol

from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import Event


class EngineStage(Protocol):
    async def run(self, ctx: EngineContext) -> list[Event]: ...
