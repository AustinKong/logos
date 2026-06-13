from datetime import datetime
from uuid import UUID

from api.modules.sessions.errors import SessionNotFoundError
from api.modules.sessions.models.events import Event
from api.modules.sessions.models.sessions import Session
from api.modules.sessions.repository import SessionRepository


class SessionService:
    def __init__(self, repository: SessionRepository) -> None:
        self._repository = repository

    def create_session(self, prompt: str) -> Session:
        return self._repository.create(prompt=prompt)

    def get_session(self, session_id: UUID) -> Session:
        session = self._repository.get(session_id)
        if session is None:
            raise SessionNotFoundError()

        return session

    def list_events(self, session_id: UUID) -> list[Event]:
        self.get_session(session_id)  # Ensure session exists
        return self._repository.list_events(session_id)

    def list_events_after(self, session_id: UUID, created_at: datetime) -> list[Event]:
        self.get_session(session_id)  # Ensure session exists
        return self._repository.list_events_after(session_id, created_at)
