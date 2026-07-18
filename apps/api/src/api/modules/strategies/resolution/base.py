from typing import Protocol

from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream


class ResolutionStrategy(Protocol):
    def resolve(self, ctx: EngineContext, *, generation_runner: GenerationRunner) -> EngineOutputStream: ...
