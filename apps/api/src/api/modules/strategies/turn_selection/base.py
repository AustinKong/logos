from typing import Protocol

from api.modules.engine.models import EngineContext
from api.modules.session_configs.models.participants import Participant


class TurnSelectionStrategy(Protocol):
    def choose_participant(self, ctx: EngineContext) -> Participant | None: ...
