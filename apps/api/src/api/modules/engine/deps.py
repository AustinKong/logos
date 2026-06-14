from typing import Annotated

from fastapi import Depends

from api.modules.ai.deps import get_ai_service
from api.modules.ai.service import AIService
from api.modules.engine.engine import Engine
from api.modules.engine.service import EngineService
from api.modules.sessions.deps import get_session_service
from api.modules.sessions.service import SessionService


def get_engine(ai_service: Annotated[AIService, Depends(get_ai_service)]) -> Engine:
    return Engine(ai_service)


def get_engine_service(
    session_service: Annotated[SessionService, Depends(get_session_service)],
    engine: Annotated[Engine, Depends(get_engine)],
) -> EngineService:
    return EngineService(session_service, engine)
