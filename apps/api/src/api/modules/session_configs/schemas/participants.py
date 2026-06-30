from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.session_configs.models.participants import ParticipantType


class AgentParticipantCreate(BaseModel):
    type: Literal[ParticipantType.AGENT] = ParticipantType.AGENT
    name: str = Field(min_length=1)
    model: str = Field(min_length=1)
    system_prompt: str = Field(min_length=1)


class UserParticipantCreate(BaseModel):
    type: Literal[ParticipantType.USER] = ParticipantType.USER
    name: str = Field(min_length=1)


type ParticipantCreate = Annotated[
    AgentParticipantCreate | UserParticipantCreate,
    Field(discriminator="type"),
]


class AgentParticipantRead(BaseModel):
    id: UUID
    type: Literal[ParticipantType.AGENT] = ParticipantType.AGENT
    name: str
    created_at: datetime
    updated_at: datetime
    model: str
    system_prompt: str


class UserParticipantRead(BaseModel):
    id: UUID
    type: Literal[ParticipantType.USER] = ParticipantType.USER
    name: str
    created_at: datetime
    updated_at: datetime


type ParticipantRead = Annotated[
    AgentParticipantRead | UserParticipantRead,
    Field(discriminator="type"),
]
