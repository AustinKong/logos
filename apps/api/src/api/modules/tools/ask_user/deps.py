from typing import Annotated

from fastapi import Depends

from api.deps import DbDep, VectorDbDep
from api.modules.ai.deps import get_ai_service
from api.modules.ai.service import AIService
from api.modules.sessions.deps import get_session_service
from api.modules.sessions.service import SessionService
from api.modules.tools.ask_user.cache import AskUserCacheRepository
from api.modules.tools.ask_user.service import AskUserService


def get_ask_user_cache_repository(vector_db: VectorDbDep) -> AskUserCacheRepository:
    return AskUserCacheRepository(vector_db=vector_db)


def get_ask_user_service(
    db: DbDep,
    session_service: Annotated[SessionService, Depends(get_session_service)],
    ai_service: Annotated[AIService, Depends(get_ai_service)],
    cache_repository: Annotated[AskUserCacheRepository, Depends(get_ask_user_cache_repository)],
) -> AskUserService:
    return AskUserService(
        db=db,
        session_service=session_service,
        ai_service=ai_service,
        cache_repository=cache_repository,
    )
