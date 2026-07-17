from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends

from api.modules.engine.background import run_session_until_blocked_background
from api.modules.sessions.adapters.events import ask_user_completed_event_read_from_event
from api.modules.sessions.schemas.events import AskUserCompletedEventRead
from api.modules.streaming.deps import SESSION_EVENT_STREAM, get_streaming_service
from api.modules.streaming.service import StreamingService
from api.modules.tools.ask_user.deps import get_ask_user_service
from api.modules.tools.ask_user.schemas import AskUserAnswerRequest
from api.modules.tools.ask_user.service import AskUserService

router = APIRouter(prefix="/ask-user", tags=["ask-user"])


@router.post("/{started_event_id}/answer", operation_id="answerAskUser", response_model=AskUserCompletedEventRead)
async def answer_ask_user(
    started_event_id: UUID,
    payload: AskUserAnswerRequest,
    background_tasks: BackgroundTasks,
    ask_user_service: Annotated[AskUserService, Depends(get_ask_user_service)],
    streaming_service: Annotated[StreamingService, Depends(get_streaming_service)],
) -> AskUserCompletedEventRead:
    event = await ask_user_service.answer(
        started_event_id=started_event_id,
        answer_kind=payload.answer_kind,
        answer=payload.answer,
    )
    await streaming_service.publish(SESSION_EVENT_STREAM, event.session_id, event)
    background_tasks.add_task(run_session_until_blocked_background, event.session_id)
    return ask_user_completed_event_read_from_event(event)
