from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.sessions.models.events import (
    ResolutionCompletedEvent,
    ResolutionStartedEvent,
    SessionCompletedEvent,
)
from api.modules.strategies.resolution.base import ResolutionStrategy


class ResolutionStage:
    def __init__(self, *, resolution_strategy: ResolutionStrategy) -> None:
        self._resolution_strategy = resolution_strategy

    async def run(self, ctx: EngineContext) -> EngineOutputStream:
        if any(isinstance(event, ResolutionCompletedEvent) for event in ctx.events):
            yield SessionCompletedEvent(session_id=ctx.session_id)
            return

        if not any(isinstance(event, ResolutionStartedEvent) for event in ctx.events):
            yield ResolutionStartedEvent(session_id=ctx.session_id)
            return

        async for output in self._resolution_strategy.resolve(ctx):
            yield output

        yield SessionCompletedEvent(session_id=ctx.session_id)
