from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.strategies.validation.base import ValidationStrategy


class ValidationStage:
    def __init__(self, *, validation_strategy: ValidationStrategy) -> None:
        self._validation_strategy = validation_strategy

    async def run(self, ctx: EngineContext) -> EngineOutputStream:
        async for output in self._validation_strategy.validate(ctx):
            yield output
