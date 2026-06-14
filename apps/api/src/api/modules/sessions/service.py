from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlAlchemyDb
from sqlalchemy.orm import selectinload

from api.modules.sessions.errors import SessionNotFoundError
from api.modules.sessions.models.events import Event, SessionStartedEvent
from api.modules.sessions.models.sessions import Session
from api.modules.sessions.repository import SessionRepository


class SessionService:
    def __init__(self, db: SqlAlchemyDb, repository: SessionRepository) -> None:
        self._db = db
        self._repository = repository

    def create_session(self, prompt: str) -> Session:
        session = Session(prompt=prompt)
        self._db.add(session)
        self._db.flush()

        self._db.add(SessionStartedEvent(session_id=session.id))
        self._db.commit()

        return session

    def get_session(self, session_id: UUID) -> Session:
        statement = select(Session).where(Session.id == session_id).options(selectinload(Session.participants))
        session = self._db.execute(statement).scalar_one_or_none()
        if session is None:
            raise SessionNotFoundError()

        return session

    def list_events(self, session_id: UUID) -> list[Event]:
        self.get_session(session_id)  # Ensure session exists
        return self._repository.list_events(session_id)

    def list_events_after(self, session_id: UUID, created_at: datetime) -> list[Event]:
        self.get_session(session_id)  # Ensure session exists
        return self._repository.list_events_after(session_id, created_at)
