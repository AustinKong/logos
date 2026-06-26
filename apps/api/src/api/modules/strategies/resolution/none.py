from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.sessions.models.events import SessionCompletedEvent


class NoneResolutionStrategy:
    async def resolve(self, ctx: EngineContext) -> EngineOutputStream:
        yield SessionCompletedEvent(session_id=ctx.session.id)
