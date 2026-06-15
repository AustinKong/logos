from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import Event
from api.modules.strategies.resolution.base import ResolutionStrategy


class ResolutionStage:
    def __init__(self, *, resolution_strategy: ResolutionStrategy) -> None:
        self._resolution_strategy = resolution_strategy

    async def run(self, ctx: EngineContext) -> list[Event]:
        return await self._resolution_strategy.resolve(ctx)
