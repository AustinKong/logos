from collections.abc import Sequence

from api.modules.engine.timeline.turns import Turn


class FullHistoryStrategy:
    def select_turns(self, turns: Sequence[Turn]) -> list[Turn]:
        return list(turns)
