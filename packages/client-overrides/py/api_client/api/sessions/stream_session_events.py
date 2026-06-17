import json
from collections.abc import AsyncIterator, Iterator
from typing import Any
from urllib.parse import quote
from uuid import UUID

from httpx_sse import aconnect_sse, connect_sse

from ...client import AuthenticatedClient, Client
from ...models.event_read import EventRead
from ...models.participant_message_event_read import ParticipantMessageEventRead
from ...models.participant_removed_event_read import ParticipantRemovedEventRead
from ...models.participant_vote_event_read import ParticipantVoteEventRead
from ...models.resolution_created_event_read import ResolutionCreatedEventRead
from ...models.session_completed_event_read import SessionCompletedEventRead
from ...models.session_started_event_read import SessionStartedEventRead


def _get_kwargs(session_id: UUID) -> dict[str, Any]:
    return {
        "method": "get",
        "url": "/sessions/{session_id}/stream".format(
            session_id=quote(str(session_id), safe=""),
        ),
        "headers": {
            "Accept": "text/event-stream",
        },
    }


def _event_from_data(data: str) -> EventRead:
    event_data = json.loads(data)
    event_type = event_data.get("type")

    match event_type:
        case "session.started":
            return SessionStartedEventRead.from_dict(event_data)
        case "session.completed":
            return SessionCompletedEventRead.from_dict(event_data)
        case "participant.message":
            return ParticipantMessageEventRead.from_dict(event_data)
        case "participant.vote":
            return ParticipantVoteEventRead.from_dict(event_data)
        case "participant.removed":
            return ParticipantRemovedEventRead.from_dict(event_data)
        case "resolution.created":
            return ResolutionCreatedEventRead.from_dict(event_data)

    raise ValueError(f"Unsupported event type: {event_type}")


def sync(
    session_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Iterator[EventRead]:
    """Stream session events as parsed event records."""
    kwargs = _get_kwargs(session_id)

    with connect_sse(client.get_httpx_client(), **kwargs) as event_source:
        event_source.response.raise_for_status()
        for event in event_source.iter_sse():
            yield _event_from_data(event.data)


async def asyncio(
    session_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> AsyncIterator[EventRead]:
    """Stream session events as parsed event records."""
    kwargs = _get_kwargs(session_id)

    async with aconnect_sse(client.get_async_httpx_client(), **kwargs) as event_source:
        event_source.response.raise_for_status()
        async for event in event_source.aiter_sse():
            yield _event_from_data(event.data)
