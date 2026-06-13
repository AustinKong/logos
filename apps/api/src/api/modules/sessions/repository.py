from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import selectinload

from api.modules.sessions.models.events import Event, SessionStartedEvent
from api.modules.sessions.models.sessions import Session


class SessionRepository:
    def __init__(self, db: SQLAlchemySession) -> None:
        self._db = db

    def create(self, prompt: str) -> Session:
        session = Session(prompt=prompt)
        self._db.add(session)
        self._db.flush()

        self._db.add(
            SessionStartedEvent(
                session_id=session.id,
            )
        )
        self._db.commit()
        return session

    def get(self, session_id: UUID) -> Session | None:
        statement = select(Session).where(Session.id == session_id).options(selectinload(Session.participants))
        return self._db.execute(statement).scalar_one_or_none()

    def list_events(self, session_id: UUID) -> list[Event]:
        statement = select(Event).where(Event.session_id == session_id).order_by(Event.created_at, Event.id)
        return list(self._db.execute(statement).scalars())

    def list_events_after(self, session_id: UUID, created_at: datetime) -> list[Event]:
        statement = (
            select(Event)
            .where(Event.session_id == session_id)
            .where(Event.created_at > created_at)
            .order_by(Event.created_at, Event.id)
        )
        return list(self._db.execute(statement).scalars())
