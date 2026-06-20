from api.modules.engine.models import EngineContext, EngineOutputStream


class AllowAllValidationStrategy:
    async def validate(self, ctx: EngineContext) -> EngineOutputStream:
        for output in ():
            yield output
