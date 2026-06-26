from typing import Annotated

from fastapi import Depends

from api.modules.ai.deps import get_ai_service
from api.modules.ai.service import AIService
from api.modules.engine.engine import Engine
from api.modules.engine.service import EngineService
from api.modules.sessions.deps import get_session_service
from api.modules.sessions.service import SessionService
from api.modules.strategies.deps import get_strategy_resolver
from api.modules.strategies.resolver import StrategyResolver
from api.modules.streaming.deps import get_streaming_service
from api.modules.streaming.service import StreamingService


def get_engine(
    ai_service: Annotated[AIService, Depends(get_ai_service)],
    strategy_resolver: Annotated[StrategyResolver, Depends(get_strategy_resolver)],
) -> Engine:
    return Engine(ai_service=ai_service, strategy_resolver=strategy_resolver)


def get_engine_service(
    session_service: Annotated[SessionService, Depends(get_session_service)],
    streaming_service: Annotated[StreamingService, Depends(get_streaming_service)],
    engine: Annotated[Engine, Depends(get_engine)],
) -> EngineService:
    return EngineService(session_service, streaming_service, engine)
