from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import Event


class AllowAllValidationStrategy:
    async def validate(self, ctx: EngineContext) -> list[Event]:
        return []
