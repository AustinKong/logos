from collections.abc import AsyncIterator
from uuid import UUID

from api_client import Client
from api_client.api.sessions.stream_session_events import asyncio as stream_session_events
from api_client.models.participant_message_event_read import ParticipantMessageEventRead
from api_client.models.resolution_created_event_read import ResolutionCreatedEventRead
from api_client.models.session_completed_event_read import SessionCompletedEventRead

type RenderableSessionEvent = ParticipantMessageEventRead | ResolutionCreatedEventRead | SessionCompletedEventRead


class SessionLoader:
    def __init__(self, *, client: Client) -> None:
        self._client = client

    async def stream_events(self, *, session_id: UUID) -> AsyncIterator[RenderableSessionEvent]:
        async for event in stream_session_events(session_id, client=self._client):
            if isinstance(event, ParticipantMessageEventRead | ResolutionCreatedEventRead | SessionCompletedEventRead):
                yield event

            if isinstance(event, SessionCompletedEventRead):
                break
