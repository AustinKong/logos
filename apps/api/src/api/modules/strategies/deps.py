from typing import Annotated

from fastapi import Depends

from api.modules.ai.deps import get_ai_service
from api.modules.ai.service import AIService
from api.modules.strategies.resolver import StrategyResolver


def get_strategy_resolver(ai_service: Annotated[AIService, Depends(get_ai_service)]) -> StrategyResolver:
    return StrategyResolver(ai_service=ai_service)
