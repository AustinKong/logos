from typing import Annotated

from fastapi import Depends

from api.deps import DbDep
from api.modules.sessions.repository import SessionRepository
from api.modules.sessions.service import SessionService


def get_session_repository(db: DbDep) -> SessionRepository:
    return SessionRepository(db)


def get_session_service(
    db: DbDep,
    repository: Annotated[SessionRepository, Depends(get_session_repository)],
) -> SessionService:
    return SessionService(db, repository)
