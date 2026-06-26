from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.session_configs.schemas.participants import ParticipantRead
from api.modules.sessions.models.events import EventType


class EventReadBase(BaseModel):
    id: UUID
    session_id: UUID
    created_at: datetime
    updated_at: datetime


class SessionStartedEventRead(EventReadBase):
    type: Literal[EventType.SESSION_STARTED]


class SessionCompletedEventRead(EventReadBase):
    type: Literal[EventType.SESSION_COMPLETED]


class MessageStartedEventRead(EventReadBase):
    type: Literal[EventType.MESSAGE_STARTED]
    message_id: UUID
    sender: ParticipantRead


class MessageCompletedEventRead(EventReadBase):
    type: Literal[EventType.MESSAGE_COMPLETED]
    message_id: UUID
    content: str


class ParticipantVoteEventRead(EventReadBase):
    type: Literal[EventType.PARTICIPANT_VOTE]
    voter: ParticipantRead
    target: ParticipantRead
    reason: str


class ParticipantRemovedEventRead(EventReadBase):
    type: Literal[EventType.PARTICIPANT_REMOVED]
    removed: ParticipantRead


class ResolutionCreatedEventRead(EventReadBase):
    type: Literal[EventType.RESOLUTION_CREATED]
    resolution: str


type EventRead = Annotated[
    SessionStartedEventRead
    | SessionCompletedEventRead
    | MessageStartedEventRead
    | MessageCompletedEventRead
    | ParticipantVoteEventRead
    | ParticipantRemovedEventRead
    | ResolutionCreatedEventRead,
    Field(discriminator="type"),
]


class TokenRead(BaseModel):
    correlation_id: UUID
    content: str
