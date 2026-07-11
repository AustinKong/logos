from collections.abc import Sequence

from api.modules.engine.timeline.turns import Turn
from api.modules.strategies.history.configs import SlidingWindowHistoryConfig


class SlidingWindowHistoryStrategy:
    def __init__(self, *, config: SlidingWindowHistoryConfig) -> None:
        self._config = config

    def select_turns(self, turns: Sequence[Turn]) -> list[Turn]:
        return list(turns[-self._config.window_size :])
