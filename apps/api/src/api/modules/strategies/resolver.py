from typing import assert_never

from api.modules.ai.service import AIService
from api.modules.sessions.models.sessions import Session
from api.modules.strategies.history.base import HistoryStrategy
from api.modules.strategies.history.configs import HistoryMode
from api.modules.strategies.history.full import FullHistoryStrategy
from api.modules.strategies.history.sliding_window import SlidingWindowHistoryStrategy
from api.modules.strategies.resolution.base import ResolutionStrategy
from api.modules.strategies.resolution.configs import (
    JudgeResolutionConfig,
    NoneResolutionConfig,
)
from api.modules.strategies.resolution.judge import JudgeResolutionStrategy
from api.modules.strategies.resolution.none import NoneResolutionStrategy
from api.modules.strategies.turn_selection.base import TurnSelectionStrategy
from api.modules.strategies.turn_selection.configs import (
    RoundRobinTurnSelectionConfig,
    ShuffledTurnSelectionConfig,
)
from api.modules.strategies.turn_selection.round_robin import RoundRobinTurnSelectionStrategy
from api.modules.strategies.turn_selection.shuffled import ShuffledTurnSelectionStrategy


class StrategyResolver:
    def __init__(self, *, ai_service: AIService) -> None:
        self._ai_service = ai_service

    def turn_selection(self, session: Session) -> TurnSelectionStrategy:
        config = session.config.turn_selection_config
        match config:
            case RoundRobinTurnSelectionConfig():
                return RoundRobinTurnSelectionStrategy()
            case ShuffledTurnSelectionConfig():
                return ShuffledTurnSelectionStrategy()
            case _ as never:
                assert_never(never)

    def history(self, session: Session) -> HistoryStrategy:
        config = session.config.history_config
        match config.mode:
            case HistoryMode.FULL:
                return FullHistoryStrategy()
            case HistoryMode.SLIDING_WINDOW:
                return SlidingWindowHistoryStrategy(config=config)
            case _ as never:
                assert_never(never)

    def resolution(self, session: Session) -> ResolutionStrategy:
        config = session.config.resolution_config
        match config:
            case JudgeResolutionConfig():
                return JudgeResolutionStrategy(
                    ai_service=self._ai_service,
                    config=config,
                )
            case NoneResolutionConfig():
                return NoneResolutionStrategy()
            case _ as never:
                assert_never(never)
