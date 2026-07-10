from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from api.modules.session_configs.schemas.participants import ParticipantRead
from api.modules.sessions.models.events import EventType
from api.modules.sessions.schemas.base import EventReadBase
from api.modules.tools.ask_user.models import AskUserAnswerKind


class AskUserAnswerRequest(BaseModel):
    answer_kind: AskUserAnswerKind
    answer: str


class AskUserStartedEventRead(EventReadBase):
    type: Literal[EventType.ASK_USER_STARTED]
    ask_user_id: UUID
    sender: ParticipantRead
    question: str
    options: list[str]
    requires_user_input: bool


class AskUserCompletedEventRead(EventReadBase):
    type: Literal[EventType.ASK_USER_COMPLETED]
    ask_user_id: UUID
    answer_kind: AskUserAnswerKind
    answer: str
