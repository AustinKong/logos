from typing import Protocol

from api.modules.engine.models import EngineContext, EngineOutputStream


class ValidationStrategy(Protocol):
    def validate(self, ctx: EngineContext) -> EngineOutputStream: ...
