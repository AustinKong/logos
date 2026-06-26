from api.modules.ai.service import AIService
from api.modules.sessions.models.sessions import Session
from api.modules.strategies.context.base import ContextStrategy
from api.modules.strategies.context.configs import ContextMode
from api.modules.strategies.context.full import FullContextStrategy
from api.modules.strategies.resolution.base import ResolutionStrategy
from api.modules.strategies.resolution.configs import (
    JudgeResolutionConfig,
    NoneResolutionConfig,
)
from api.modules.strategies.resolution.judge import JudgeResolutionStrategy
from api.modules.strategies.resolution.none import NoneResolutionStrategy
from api.modules.strategies.turn_selection.base import TurnSelectionStrategy
from api.modules.strategies.turn_selection.configs import TurnSelectionMode
from api.modules.strategies.turn_selection.round_robin import RoundRobinTurnSelectionStrategy
from api.modules.strategies.validation.allow_all import AllowAllValidationStrategy
from api.modules.strategies.validation.base import ValidationStrategy
from api.modules.strategies.validation.configs import ValidationMode


class StrategyResolver:
    def __init__(self, *, ai_service: AIService) -> None:
        self._ai_service = ai_service

    def turn_selection(self, session: Session) -> TurnSelectionStrategy:
        config = session.config.turn_selection_config
        match config.mode:
            case TurnSelectionMode.ROUND_ROBIN:
                return RoundRobinTurnSelectionStrategy()
        # TODO: Custom error for these
        raise ValueError(f"Unsupported turn selection mode: {config.mode}")

    def context(self, session: Session) -> ContextStrategy:
        config = session.config.context_config
        match config.mode:
            case ContextMode.FULL:
                return FullContextStrategy()
        raise ValueError(f"Unsupported context mode: {config.mode}")

    def validation(self, session: Session) -> ValidationStrategy:
        config = session.config.validation_config
        match config.mode:
            case ValidationMode.ALLOW_ALL:
                return AllowAllValidationStrategy()
        raise ValueError(f"Unsupported validation mode: {config.mode}")

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
        raise ValueError(f"Unsupported resolution mode: {config.mode}")
