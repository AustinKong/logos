import json
from collections.abc import AsyncIterator, Iterator
from typing import Any
from urllib.parse import quote
from uuid import UUID

from attrs import define as _attrs_define
from httpx_sse import aconnect_sse, connect_sse

from ...client import AuthenticatedClient, Client


@_attrs_define
class TokenRead:
    stream_id: UUID
    content: str


def _get_kwargs(session_id: UUID, *, stream_id: UUID) -> dict[str, Any]:
    return {
        "method": "get",
        "url": "/sessions/{session_id}/tokens/stream".format(
            session_id=quote(str(session_id), safe=""),
        ),
        "params": {
            "stream_id": str(stream_id),
        },
        "headers": {
            "Accept": "text/event-stream",
        },
    }


def _token_from_data(data: str) -> TokenRead:
    token_data = json.loads(data)
    return TokenRead(
        stream_id=UUID(token_data["stream_id"]),
        content=token_data["content"],
    )


def sync(
    session_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    stream_id: UUID,
) -> Iterator[TokenRead]:
    """Stream session tokens as parsed token records."""
    kwargs = _get_kwargs(session_id, stream_id=stream_id)

    with connect_sse(client.get_httpx_client(), **kwargs) as event_source:
        event_source.response.raise_for_status()
        for event in event_source.iter_sse():
            yield _token_from_data(event.data)


async def asyncio(
    session_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    stream_id: UUID,
) -> AsyncIterator[TokenRead]:
    """Stream session tokens as parsed token records."""
    kwargs = _get_kwargs(session_id, stream_id=stream_id)

    async with aconnect_sse(client.get_async_httpx_client(), **kwargs) as event_source:
        event_source.response.raise_for_status()
        async for event in event_source.aiter_sse():
            yield _token_from_data(event.data)
