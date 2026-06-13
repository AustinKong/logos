import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sse_starlette import EventSourceResponse

from api.modules.sessions.adapters import event_read_from_event, session_read_from_session
from api.modules.sessions.deps import get_session_service
from api.modules.sessions.schemas import EventRead, SessionCreate, SessionRead
from api.modules.sessions.service import SessionService
from api.shared.responses import ServerSentEventResponse
from api.shared.time import UTC_EPOCH

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", operation_id="createSession", response_model=SessionRead, status_code=201)
def create_session(
    payload: SessionCreate,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionRead:
    return session_read_from_session(service.create_session(prompt=payload.prompt))


@router.get("/{session_id}", operation_id="getSession", response_model=SessionRead)
def get_session(
    session_id: UUID,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionRead:
    return session_read_from_session(service.get_session(session_id))


@router.get("/{session_id}/events", operation_id="listSessionEvents", response_model=list[EventRead])
def list_session_events(
    session_id: UUID,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> list[EventRead]:
    return [event_read_from_event(event) for event in service.list_events(session_id)]


@router.get("/{session_id}/stream", operation_id="streamSessionEvents", response_class=ServerSentEventResponse)
async def stream_session_events(
    session_id: UUID,
    request: Request,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> EventSourceResponse:
    async def events():
        last_event_created_at = UTC_EPOCH

        while not await request.is_disconnected():
            batch = service.list_events_after(session_id, last_event_created_at)
            for event in batch:
                event_response = event_read_from_event(event)
                yield {
                    "data": event_response.model_dump_json(),
                }

            if batch:
                last_event_created_at = batch[-1].created_at

            await asyncio.sleep(1)

    return ServerSentEventResponse(events())
