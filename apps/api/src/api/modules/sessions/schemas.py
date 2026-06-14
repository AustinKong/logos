from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.sessions.models.events import EventType
from api.modules.sessions.models.participants import ParticipantType


class AgentParticipantCreate(BaseModel):
    name: str
    model: str
    system_prompt: str


class SessionCreate(BaseModel):
    prompt: str
    agents: list[AgentParticipantCreate] = Field(default_factory=list)


class ParticipantRead(BaseModel):
    id: UUID
    type: ParticipantType
    name: str
    created_at: datetime
    updated_at: datetime


class SessionRead(BaseModel):
    id: UUID
    prompt: str
    created_at: datetime
    updated_at: datetime
    participants: list[ParticipantRead]


class EventReadBase(BaseModel):
    id: UUID
    session_id: UUID
    created_at: datetime
    updated_at: datetime


class SessionStartedEventRead(EventReadBase):
    type: Literal[EventType.SESSION_STARTED]


class SessionCompletedEventRead(EventReadBase):
    type: Literal[EventType.SESSION_COMPLETED]


class ParticipantMessageEventRead(EventReadBase):
    type: Literal[EventType.PARTICIPANT_MESSAGE]
    sender_id: UUID
    content: str


class ParticipantVoteEventRead(EventReadBase):
    type: Literal[EventType.PARTICIPANT_VOTE]
    voter_id: UUID
    target_id: UUID
    reason: str


class ParticipantRemovedEventRead(EventReadBase):
    type: Literal[EventType.PARTICIPANT_REMOVED]
    removed_id: UUID


EventRead = Annotated[
    SessionStartedEventRead
    | SessionCompletedEventRead
    | ParticipantMessageEventRead
    | ParticipantVoteEventRead
    | ParticipantRemovedEventRead,
    Field(discriminator="type"),
]
