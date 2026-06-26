from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.sessions.models.sessions import SessionStatus
from api.modules.sessions.schemas.configs import (
    ContextConfigCreate,
    ResolutionConfigCreate,
    TurnSelectionConfigCreate,
    ValidationConfigCreate,
)
from api.modules.sessions.schemas.participants import AgentParticipantCreate, ParticipantRead


class SessionCreate(BaseModel):
    prompt: str
    agents: list[AgentParticipantCreate] = Field(min_length=1)
    turn_selection: TurnSelectionConfigCreate
    context: ContextConfigCreate
    validation: ValidationConfigCreate
    resolution: ResolutionConfigCreate


class SessionRead(BaseModel):
    id: UUID
    prompt: str
    created_at: datetime
    updated_at: datetime
    participants: list[ParticipantRead]


class SessionSummaryRead(BaseModel):
    id: UUID
    prompt: str
    created_at: datetime
    updated_at: datetime
    participant_count: int
    status: SessionStatus
