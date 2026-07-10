from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.session_configs.schemas.participants import ParticipantRead
from api.modules.sessions.models.events import EventType
from api.modules.sessions.schemas.base import EventReadBase
from api.modules.tools.ask_user.schemas import AskUserCompletedEventRead, AskUserStartedEventRead


class SessionStartedEventRead(EventReadBase):
    type: Literal[EventType.SESSION_STARTED]


class SessionCompletedEventRead(EventReadBase):
    type: Literal[EventType.SESSION_COMPLETED]


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


class MessageStartedEventRead(EventReadBase):
    type: Literal[EventType.MESSAGE_STARTED]
    message_id: UUID
    sender: ParticipantRead


class MessageCompletedEventRead(EventReadBase):
    type: Literal[EventType.MESSAGE_COMPLETED]
    message_id: UUID
    content: str


class ReasoningStartedEventRead(EventReadBase):
    type: Literal[EventType.REASONING_STARTED]
    reasoning_id: UUID
    sender: ParticipantRead


class ReasoningCompletedEventRead(EventReadBase):
    type: Literal[EventType.REASONING_COMPLETED]
    reasoning_id: UUID
    content: str


type EventRead = Annotated[
    SessionStartedEventRead
    | SessionCompletedEventRead
    | ProposalStartedEventRead
    | ProposalCompletedEventRead
    | DebateRoundStartedEventRead
    | DebateRoundCompletedEventRead
    | ResolutionStartedEventRead
    | ResolutionCompletedEventRead
    | MessageStartedEventRead
    | MessageCompletedEventRead
    | ReasoningStartedEventRead
    | ReasoningCompletedEventRead
    | AskUserStartedEventRead
    | AskUserCompletedEventRead,
    Field(discriminator="type"),
]


class TokenRead(BaseModel):
    correlation_id: UUID
    content: str
