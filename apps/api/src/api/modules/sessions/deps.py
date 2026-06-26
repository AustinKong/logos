from typing import Annotated

from fastapi import Depends

from api.deps import DbDep
from api.modules.session_configs.deps import get_session_config_service
from api.modules.session_configs.service import SessionConfigService
from api.modules.sessions.repository import SessionRepository
from api.modules.sessions.service import SessionService


def get_session_repository(db: DbDep) -> SessionRepository:
    return SessionRepository(db)


def get_session_service(
    db: DbDep,
    repository: Annotated[SessionRepository, Depends(get_session_repository)],
    session_config_service: Annotated[SessionConfigService, Depends(get_session_config_service)],
) -> SessionService:
    return SessionService(db, repository, session_config_service)
