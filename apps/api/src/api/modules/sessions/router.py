from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sse_starlette import EventSourceResponse

from api.modules.engine.adapters import token_read_from_token
from api.modules.engine.background import run_session_until_blocked_background
from api.modules.sessions.adapters.configs import (
    debate_config_from_create,
    participant_data_from_debate_create,
    participant_data_from_resolution_create,
    proposal_config_from_create,
    resolution_config_from_create,
)
from api.modules.sessions.adapters.events import event_read_from_event
from api.modules.sessions.adapters.sessions import (
    session_read_from_session,
    session_summary_read_from_summary,
)
from api.modules.sessions.deps import get_session_service
from api.modules.sessions.models.events import SessionCompletedEvent
from api.modules.sessions.schemas.events import EventRead
from api.modules.sessions.schemas.sessions import (
    SessionCreate,
    SessionExportResponse,
    SessionRead,
    SessionSummaryRead,
)
from api.modules.sessions.service import SessionService
from api.modules.streaming.deps import SESSION_EVENT_STREAM, TOKEN_STREAM, get_streaming_service
from api.modules.streaming.service import StreamingService
from api.shared.responses import ServerSentEventResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", operation_id="createSession", response_model=SessionRead, status_code=201)
def create_session(
    payload: SessionCreate,
    background_tasks: BackgroundTasks,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionRead:
    config = payload.config
    session = service.create_session(
        prompt=config.prompt,
        seed=config.seed,
        proposal_config=proposal_config_from_create(config.proposal),
        debate_config=debate_config_from_create(config.debate),
        participants=[
            *participant_data_from_debate_create(config.debate),
            *participant_data_from_resolution_create(config.resolution),
        ],
        resolution_config=resolution_config_from_create(config.resolution),
    )
    background_tasks.add_task(run_session_until_blocked_background, session.id)
    return session_read_from_session(session)


@router.get("", operation_id="listSessions", response_model=list[SessionSummaryRead])
def list_sessions(
    service: Annotated[SessionService, Depends(get_session_service)],
) -> list[SessionSummaryRead]:
    return [session_summary_read_from_summary(summary) for summary in service.list_session_summaries()]


@router.get("/{session_id}", operation_id="getSession", response_model=SessionRead)
def get_session(
    session_id: UUID,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionRead:
    session = service.get_session(session_id)
    return session_read_from_session(session)


@router.post("/{session_id}/export", operation_id="exportSession", response_model=SessionExportResponse)
def export_session(
    session_id: UUID,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionExportResponse:
    export_path = service.export_session(session_id)
    return SessionExportResponse(path=str(export_path))


@router.get("/{session_id}/events", operation_id="listSessionEvents", response_model=list[EventRead])
def list_session_events(
    session_id: UUID,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> list[EventRead]:
    return [event_read_from_event(event) for event in service.list_events(session_id)]


@router.get("/{session_id}/events/stream", operation_id="streamSessionEvents", response_class=ServerSentEventResponse)
async def stream_session_events(
    session_id: UUID,
    request: Request,
    session_service: Annotated[SessionService, Depends(get_session_service)],
    streaming_service: Annotated[StreamingService, Depends(get_streaming_service)],
    after_event_id: UUID | None = None,
) -> EventSourceResponse:
    session_service.get_session(session_id)
    event_stream = await streaming_service.subscribe(
        SESSION_EVENT_STREAM,
        session_id,
        after=(lambda event: event.id == after_event_id) if after_event_id is not None else None,
    )

    async def events():
        async with event_stream:
            async for event in event_stream:
                if await request.is_disconnected():
                    return

                yield {
                    "data": event_read_from_event(event).model_dump_json(),
                }
                if isinstance(event, SessionCompletedEvent):
                    return

    return ServerSentEventResponse(events())


@router.get("/{session_id}/tokens/stream", operation_id="streamSessionTokens", response_class=ServerSentEventResponse)
async def stream_session_tokens(
    session_id: UUID,
    stream_id: UUID,
    request: Request,
    session_service: Annotated[SessionService, Depends(get_session_service)],
    streaming_service: Annotated[StreamingService, Depends(get_streaming_service)],
) -> EventSourceResponse:
    session_service.get_session(session_id)
    token_stream = await streaming_service.subscribe(TOKEN_STREAM, stream_id)

    async def tokens():
        async with token_stream:
            async for token in token_stream:
                if await request.is_disconnected():
                    return

                yield {
                    "data": token_read_from_token(token).model_dump_json(),
                }

    return ServerSentEventResponse(tokens())
