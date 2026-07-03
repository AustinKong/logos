from uuid import UUID

from api.modules.engine.engine import Engine
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.sessions.models.events import (
    Event,
    MessageCompletedEvent,
    MessageStartedEvent,
    ReasoningCompletedEvent,
    ReasoningStartedEvent,
    SessionCompletedEvent,
    SessionStartedEvent,
)
from api.modules.sessions.service import SessionService
from api.modules.streaming.deps import SESSION_EVENT_STREAM, TOKEN_STREAM
from api.modules.streaming.service import StreamingService


class EngineService:
    def __init__(
        self,
        session_service: SessionService,
        streaming_service: StreamingService,
        engine: Engine,
    ) -> None:
        self._session_service = session_service
        self._streaming_service = streaming_service
        self._engine = engine

    async def step(self, session_id: UUID) -> EngineOutputStream:
        session = self._session_service.get_session(session_id)
        events = self._session_service.list_events(session_id)
        ctx = EngineContext(
            session=session,
            participants=session.config.participants,
            events=events,
        )

        async for output in self._engine.step(ctx):
            if isinstance(output, Event):
                await self._open_streams_for_event(output)
                self._session_service.append_events(session_id, [output])
                await self._streaming_service.publish(SESSION_EVENT_STREAM, output.session_id, output)
                await self._close_streams_for_event(output)
            else:
                await self._streaming_service.publish(TOKEN_STREAM, output.correlation_id, output)

            yield output

    async def _open_streams_for_event(self, event: Event) -> None:
        match event:
            case SessionStartedEvent():
                await self._streaming_service.open(SESSION_EVENT_STREAM, event.session_id)
            case MessageStartedEvent():
                await self._streaming_service.open(TOKEN_STREAM, event.message_id)
            case ReasoningStartedEvent():
                await self._streaming_service.open(TOKEN_STREAM, event.reasoning_id)
            case _:
                return

    async def _close_streams_for_event(self, event: Event) -> None:
        match event:
            case SessionCompletedEvent():
                await self._streaming_service.close(SESSION_EVENT_STREAM, event.session_id)
            case MessageCompletedEvent():
                await self._streaming_service.close(TOKEN_STREAM, event.message_id)
            case ReasoningCompletedEvent():
                await self._streaming_service.close(TOKEN_STREAM, event.reasoning_id)
            case _:
                return

    async def run_until_blocked(self, session_id: UUID) -> None:
        while True:
            has_output = False
            async for output in self.step(session_id):
                has_output = True
                if isinstance(output, SessionCompletedEvent):
                    return

            if not has_output:
                return
