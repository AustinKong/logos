from collections.abc import Sequence
from typing import Protocol

from api.modules.engine.timeline.turns import Turn


class HistoryStrategy(Protocol):
    def select_turns(self, turns: Sequence[Turn]) -> list[Turn]: ...
