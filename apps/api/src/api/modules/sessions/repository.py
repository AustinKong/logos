from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlAlchemyDb

from api.modules.sessions.models.events import Event


class SessionRepository:
    def __init__(self, db: SqlAlchemyDb) -> None:
        self._db = db

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
