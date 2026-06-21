from collections.abc import AsyncIterator
from uuid import UUID

from api_client import Client
from api_client.api.sessions.get_session import asyncio as get_session
from api_client.api.sessions.list_session_events import asyncio as list_session_events
from api_client.api.sessions.stream_session_events import asyncio as stream_session_events
from api_client.api.sessions.stream_session_tokens import TokenRead
from api_client.api.sessions.stream_session_tokens import asyncio as stream_session_tokens
from api_client.models.event_read import EventRead
from api_client.models.session_read import SessionRead


class SessionChatLoader:
    def __init__(self, *, client: Client) -> None:
        self._client = client

    async def get_session(self, *, session_id: UUID) -> SessionRead:
        session = await get_session(session_id, client=self._client)
        if not isinstance(session, SessionRead):
            raise RuntimeError("API returned an unexpected get session response")

        return session

    async def get_events(self, *, session_id: UUID) -> list[EventRead]:
        events = await list_session_events(session_id, client=self._client)
        if not isinstance(events, list):
            raise RuntimeError("API returned an unexpected list session events response")

        return events

    async def stream_events(
        self,
        *,
        session_id: UUID,
        after_event_id: UUID | None = None,
    ) -> AsyncIterator[EventRead]:
        async for event in stream_session_events(session_id, client=self._client, after_event_id=after_event_id):
            yield event

    async def stream_tokens(
        self,
        *,
        session_id: UUID,
        stream_id: UUID,
    ) -> AsyncIterator[TokenRead]:
        async for token in stream_session_tokens(session_id, client=self._client, stream_id=stream_id):
            yield token
