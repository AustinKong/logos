from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from sse_starlette import EventSourceResponse

from api.modules.engine.background import run_session_until_blocked_background
from api.modules.sessions.adapters import (
    event_read_from_event,
    session_read_from_session,
    token_read_from_token,
)
from api.modules.sessions.deps import get_session_service
from api.modules.sessions.models.events import SessionCompletedEvent
from api.modules.sessions.models.participants import AgentParticipantConfig
from api.modules.sessions.schemas import EventRead, SessionCreate, SessionRead
from api.modules.sessions.service import SessionService
from api.modules.streaming.deps import SESSION_EVENT_STREAM, TOKEN_STREAM, get_streaming_service
from api.modules.streaming.service import StreamingService
from api.shared.responses import ServerSentEventResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])

TEMPORARY_TEST_MODEL = "openai/gpt-4o-mini"
TEMPORARY_TEST_PROMPT = "How should engineering teams decide when to use AI agents in production workflows?"
TEMPORARY_TEST_AGENTS = [
    AgentParticipantConfig(
        name="Pragmatist",
        model=TEMPORARY_TEST_MODEL,
        system_prompt="Argue for the simplest useful implementation that proves value quickly.",
    ),
    AgentParticipantConfig(
        name="Skeptic",
        model=TEMPORARY_TEST_MODEL,
        system_prompt="Point out risks, failure modes, and missing safeguards in the implementation.",
    ),
]


@router.post("", operation_id="createSession", response_model=SessionRead, status_code=201)
def create_session(
    _payload: SessionCreate,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionRead:
    session = service.create_session(
        prompt=TEMPORARY_TEST_PROMPT,
        agents=TEMPORARY_TEST_AGENTS,
    )
    return session_read_from_session(session)


@router.get("/{session_id}", operation_id="getSession", response_model=SessionRead)
def get_session(
    session_id: UUID,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionRead:
    session = service.get_session(session_id)
    return session_read_from_session(session)


@router.get("/{session_id}/events", operation_id="listSessionEvents", response_model=list[EventRead])
def list_session_events(
    session_id: UUID,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> list[EventRead]:
    return [event_read_from_event(event) for event in service.list_events(session_id)]


@router.post(
    "/{session_id}/run-until-blocked",
    operation_id="runSessionUntilBlocked",
    status_code=status.HTTP_202_ACCEPTED,
    response_class=Response,
)
def run_session_until_blocked(
    session_id: UUID,
    background_tasks: BackgroundTasks,
) -> Response:
    background_tasks.add_task(run_session_until_blocked_background, session_id)
    return Response(status_code=status.HTTP_202_ACCEPTED)


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
