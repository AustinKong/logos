from typing import Protocol

from api.modules.engine.models import EngineContext


class HistoryStrategy(Protocol):
    def build_history(self, ctx: EngineContext) -> str | None: ...
