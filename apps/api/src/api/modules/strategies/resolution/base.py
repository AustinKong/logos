from typing import Protocol

from api.modules.engine.models import EngineContext, EngineOutputStream


class ResolutionStrategy(Protocol):
    def resolve(self, ctx: EngineContext) -> EngineOutputStream: ...
