from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.sessions.models.events import ResolutionCompletedEvent

NO_AUTOMATIC_RESOLUTION_DECISION = "No automatic resolution was configured."


class NoneResolutionStrategy:
    async def resolve(self, ctx: EngineContext, *, generation_runner: GenerationRunner) -> EngineOutputStream:
        yield ResolutionCompletedEvent(
            session_id=ctx.session_id,
            decision=NO_AUTOMATIC_RESOLUTION_DECISION,
        )
