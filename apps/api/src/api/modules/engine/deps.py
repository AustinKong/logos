from typing import Annotated

from fastapi import Depends

from api.modules.ai.deps import get_ai_service
from api.modules.ai.service import AIService
from api.modules.engine.engine import Engine
from api.modules.engine.generation import GenerationRunner
from api.modules.engine.service import EngineService
from api.modules.sessions.deps import get_session_service
from api.modules.sessions.service import SessionService
from api.modules.strategies.deps import get_strategy_resolver
from api.modules.strategies.resolver import StrategyResolver
from api.modules.streaming.deps import get_streaming_service
from api.modules.streaming.service import StreamingService
from api.modules.tools.deps import get_tool_service
from api.modules.tools.service import ToolService


def get_generation_runner(
    ai_service: Annotated[AIService, Depends(get_ai_service)],
) -> GenerationRunner:
    return GenerationRunner(ai_service=ai_service)


def get_engine(
    generation_runner: Annotated[GenerationRunner, Depends(get_generation_runner)],
    strategy_resolver: Annotated[StrategyResolver, Depends(get_strategy_resolver)],
    tool_service: Annotated[ToolService, Depends(get_tool_service)],
) -> Engine:
    return Engine(
        generation_runner=generation_runner,
        strategy_resolver=strategy_resolver,
        tool_service=tool_service,
    )


def get_engine_service(
    session_service: Annotated[SessionService, Depends(get_session_service)],
    streaming_service: Annotated[StreamingService, Depends(get_streaming_service)],
    engine: Annotated[Engine, Depends(get_engine)],
) -> EngineService:
    return EngineService(session_service, streaming_service, engine)
