import json
from collections.abc import AsyncIterator, Iterator
from typing import Any
from urllib.parse import quote
from uuid import UUID

from httpx_sse import aconnect_sse, connect_sse

from ...client import AuthenticatedClient, Client
from ...models.debate_round_completed_event_read import DebateRoundCompletedEventRead
from ...models.debate_round_started_event_read import DebateRoundStartedEventRead
from ...models.event_read import EventRead
from ...models.message_completed_event_read import MessageCompletedEventRead
from ...models.message_started_event_read import MessageStartedEventRead
from ...models.proposal_completed_event_read import ProposalCompletedEventRead
from ...models.proposal_started_event_read import ProposalStartedEventRead
from ...models.reasoning_completed_event_read import ReasoningCompletedEventRead
from ...models.reasoning_started_event_read import ReasoningStartedEventRead
from ...models.resolution_completed_event_read import ResolutionCompletedEventRead
from ...models.resolution_started_event_read import ResolutionStartedEventRead
from ...models.session_completed_event_read import SessionCompletedEventRead
from ...models.session_started_event_read import SessionStartedEventRead


def _get_kwargs(session_id: UUID, *, after_event_id: UUID | None = None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if after_event_id is not None:
        params["after_event_id"] = str(after_event_id)

    return {
        "method": "get",
        "url": "/sessions/{session_id}/events/stream".format(
            session_id=quote(str(session_id), safe=""),
        ),
        "params": params,
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
        case "proposal.started":
            return ProposalStartedEventRead.from_dict(event_data)
        case "proposal.completed":
            return ProposalCompletedEventRead.from_dict(event_data)
        case "debate_round.started":
            return DebateRoundStartedEventRead.from_dict(event_data)
        case "debate_round.completed":
            return DebateRoundCompletedEventRead.from_dict(event_data)
        case "resolution.started":
            return ResolutionStartedEventRead.from_dict(event_data)
        case "resolution.completed":
            return ResolutionCompletedEventRead.from_dict(event_data)
        case "message.started":
            return MessageStartedEventRead.from_dict(event_data)
        case "message.completed":
            return MessageCompletedEventRead.from_dict(event_data)
        case "reasoning.started":
            return ReasoningStartedEventRead.from_dict(event_data)
        case "reasoning.completed":
            return ReasoningCompletedEventRead.from_dict(event_data)

    raise ValueError(f"Unsupported event type: {event_type}")


def sync(
    session_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    after_event_id: UUID | None = None,
) -> Iterator[EventRead]:
    """Stream session events as parsed event records."""
    kwargs = _get_kwargs(session_id, after_event_id=after_event_id)

    with connect_sse(client.get_httpx_client(), **kwargs) as event_source:
        event_source.response.raise_for_status()
        for event in event_source.iter_sse():
            yield _event_from_data(event.data)


async def asyncio(
    session_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    after_event_id: UUID | None = None,
) -> AsyncIterator[EventRead]:
    """Stream session events as parsed event records."""
    kwargs = _get_kwargs(session_id, after_event_id=after_event_id)

    async with aconnect_sse(client.get_async_httpx_client(), **kwargs) as event_source:
        event_source.response.raise_for_status()
        async for event in event_source.aiter_sse():
            yield _event_from_data(event.data)
