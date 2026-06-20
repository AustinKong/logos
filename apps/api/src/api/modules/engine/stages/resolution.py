from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.strategies.resolution.base import ResolutionStrategy


class ResolutionStage:
    def __init__(self, *, resolution_strategy: ResolutionStrategy) -> None:
        self._resolution_strategy = resolution_strategy

    async def run(self, ctx: EngineContext) -> EngineOutputStream:
        async for output in self._resolution_strategy.resolve(ctx):
            yield output
