from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.session_configs.schemas.participants import ParticipantRead
from api.modules.sessions.models.events import EventType
from api.modules.tools.ask_user.models import AskUserAnswerKind


class EventReadBase(BaseModel):
    id: UUID
    session_id: UUID
    created_at: datetime
    updated_at: datetime


class SessionStartedEventRead(EventReadBase):
    type: Literal[EventType.SESSION_STARTED]


class SessionCompletedEventRead(EventReadBase):
    type: Literal[EventType.SESSION_COMPLETED]


class TurnStartedEventRead(EventReadBase):
    type: Literal[EventType.TURN_STARTED]
    participant: ParticipantRead


class TurnCompletedEventRead(EventReadBase):
    type: Literal[EventType.TURN_COMPLETED]


class ProposalStartedEventRead(EventReadBase):
    type: Literal[EventType.PROPOSAL_STARTED]


class ProposalCompletedEventRead(EventReadBase):
    type: Literal[EventType.PROPOSAL_COMPLETED]


class DebateRoundStartedEventRead(EventReadBase):
    type: Literal[EventType.DEBATE_ROUND_STARTED]
    round_number: int


class DebateRoundCompletedEventRead(EventReadBase):
    type: Literal[EventType.DEBATE_ROUND_COMPLETED]


class ResolutionStartedEventRead(EventReadBase):
    type: Literal[EventType.RESOLUTION_STARTED]


class ResolutionCompletedEventRead(EventReadBase):
    type: Literal[EventType.RESOLUTION_COMPLETED]
    decision: str


class ResolutionVoteEventRead(EventReadBase):
    type: Literal[EventType.RESOLUTION_VOTE]
    selected_participant: ParticipantRead


class MessageStartedEventRead(EventReadBase):
    type: Literal[EventType.MESSAGE_STARTED]


class MessageCompletedEventRead(EventReadBase):
    type: Literal[EventType.MESSAGE_COMPLETED]
    started_event_id: UUID
    content: str


class ReasoningStartedEventRead(EventReadBase):
    type: Literal[EventType.REASONING_STARTED]


class ReasoningCompletedEventRead(EventReadBase):
    type: Literal[EventType.REASONING_COMPLETED]
    started_event_id: UUID
    content: str


class AskUserStartedEventRead(EventReadBase):
    type: Literal[EventType.ASK_USER_STARTED]
    question: str
    options: list[str]
    requires_user_input: bool


class AskUserCompletedEventRead(EventReadBase):
    type: Literal[EventType.ASK_USER_COMPLETED]
    started_event_id: UUID
    answer_kind: AskUserAnswerKind
    answer: str


type EventRead = Annotated[
    SessionStartedEventRead
    | SessionCompletedEventRead
    | TurnStartedEventRead
    | TurnCompletedEventRead
    | ProposalStartedEventRead
    | ProposalCompletedEventRead
    | DebateRoundStartedEventRead
    | DebateRoundCompletedEventRead
    | ResolutionStartedEventRead
    | ResolutionCompletedEventRead
    | ResolutionVoteEventRead
    | MessageStartedEventRead
    | MessageCompletedEventRead
    | ReasoningStartedEventRead
    | ReasoningCompletedEventRead
    | AskUserStartedEventRead
    | AskUserCompletedEventRead,
    Field(discriminator="type"),
]
