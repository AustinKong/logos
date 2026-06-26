from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlAlchemyDb
from sqlalchemy.orm import selectinload

from api.modules.sessions.errors import SessionNotFoundError
from api.modules.sessions.models.events import Event
from api.modules.sessions.models.participants import AgentParticipant
from api.modules.sessions.models.session_configs import SessionConfig
from api.modules.sessions.models.sessions import Session, SessionSummary
from api.modules.sessions.repository import SessionRepository


class SessionService:
    def __init__(self, db: SqlAlchemyDb, repository: SessionRepository) -> None:
        self._db = db
        self._repository = repository

    def create_session(self, config: SessionConfig) -> Session:
        session = Session(
            prompt=config.prompt,
            turn_selection_config=config.turn_selection,
            context_config=config.context,
            validation_config=config.validation,
            resolution_config=config.resolution,
        )

        self._db.add(session)
        self._db.flush()

        for agent in config.agents:
            self._db.add(
                AgentParticipant(
                    session_id=session.id,
                    name=agent.name,
                    model=agent.model,
                    system_prompt=agent.system_prompt,
                )
            )

        self._db.commit()

        return self.get_session(session.id)

    def get_session(self, session_id: UUID) -> Session:
        statement = select(Session).where(Session.id == session_id).options(selectinload(Session.participants))
        session = self._db.execute(statement).scalar_one_or_none()
        if session is None:
            raise SessionNotFoundError()

        return session

    def list_session_summaries(self) -> list[SessionSummary]:
        return self._repository.list_session_summaries()

    def list_events(self, session_id: UUID) -> list[Event]:
        self.get_session(session_id)  # Ensure session exists
        return self._repository.list_events(session_id)

    def list_events_after(self, session_id: UUID, created_at: datetime) -> list[Event]:
        self.get_session(session_id)
        return self._repository.list_events_after(session_id, created_at)

    def append_events(self, session_id: UUID, events: list[Event]) -> list[Event]:
        self.get_session(session_id)

        for event in events:
            event.session_id = session_id

        self._db.add_all(events)
        self._db.commit()
        return events
