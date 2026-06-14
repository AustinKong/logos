from uuid import UUID

from api.modules.engine.engine import Engine
from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import Event
from api.modules.sessions.service import SessionService


class EngineService:
    def __init__(
        self,
        session_service: SessionService,
        engine: Engine,
    ) -> None:
        self._session_service = session_service
        self._engine = engine

    async def step(self, session_id: UUID) -> list[Event]:
        session = self._session_service.get_session(session_id)
        events = self._session_service.list_events(session_id)
        ctx = EngineContext(
            session=session,
            participants=session.participants,
            events=events,
        )

        new_events = await self._engine.step(ctx)
        if new_events:
            self._session_service.append_events(session_id, new_events)

        return new_events

    async def run_until_blocked(self, session_id: UUID) -> list[Event]:
        emitted_events: list[Event] = []

        while True:
            new_events = await self.step(session_id)
            if not new_events:
                break

            emitted_events.extend(new_events)

        return emitted_events
