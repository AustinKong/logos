from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.session_configs.models.participants import ParticipantType


class AgentParticipantCreate(BaseModel):
    type: Literal[ParticipantType.AGENT] = Field(
        ParticipantType.AGENT,
        title="Agent",
        description="AI participant that responds with the selected model and system prompt.",
    )
    name: str = Field(
        min_length=1,
        title="Name",
        description="Display name for this participant.",
    )
    model: str = Field(
        min_length=1,
        title="Model",
        description="AI model used to generate this participant's responses.",
    )
    system_prompt: str = Field(
        min_length=1,
        title="System prompt",
        description="Instructions that shape how this participant behaves.",
    )


class UserParticipantCreate(BaseModel):
    type: Literal[ParticipantType.USER] = Field(
        ParticipantType.USER,
        title="User",
        description="Human participant represented in the session.",
    )
    name: str = Field(
        min_length=1,
        title="Name",
        description="Display name for this participant.",
    )


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
