from typing import Protocol

from api.modules.engine.models import EngineContext, EngineOutputStream


class EngineStage(Protocol):
    def run(self, ctx: EngineContext) -> EngineOutputStream: ...
