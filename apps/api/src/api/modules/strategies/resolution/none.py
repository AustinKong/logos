from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.sessions.models.events import ResolutionCompletedEvent
from api.modules.strategies.resolution.configs import NoneResolutionConfig

NO_AUTOMATIC_RESOLUTION_DECISION = "No automatic resolution was configured."


class NoneResolutionStrategy:
    def __init__(self, *, config: NoneResolutionConfig) -> None:
        self._config = config

    async def resolve(self, ctx: EngineContext) -> EngineOutputStream:
        yield ResolutionCompletedEvent(
            session_id=ctx.session_id,
            decision=NO_AUTOMATIC_RESOLUTION_DECISION,
        )
