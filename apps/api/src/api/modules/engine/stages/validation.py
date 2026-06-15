from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import Event
from api.modules.strategies.validation.base import ValidationStrategy


class ValidationStage:
    def __init__(self, *, validation_strategy: ValidationStrategy) -> None:
        self._validation_strategy = validation_strategy

    async def run(self, ctx: EngineContext) -> list[Event]:
        return await self._validation_strategy.validate(ctx)
