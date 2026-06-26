from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.session_configs.schemas.configs import (
    ContextConfigCreate,
    ContextConfigRead,
    ResolutionConfigCreate,
    ResolutionConfigRead,
    TurnSelectionConfigCreate,
    TurnSelectionConfigRead,
    ValidationConfigCreate,
    ValidationConfigRead,
)
from api.modules.session_configs.schemas.participants import ParticipantCreate, ParticipantRead


class SessionConfigCreate(BaseModel):
    prompt: str = Field(min_length=1)
    participants: list[ParticipantCreate] = Field(min_length=1)
    turn_selection: TurnSelectionConfigCreate
    context: ContextConfigCreate
    validation: ValidationConfigCreate
    resolution: ResolutionConfigCreate


class SessionConfigRead(BaseModel):
    id: UUID
    prompt: str
    created_at: datetime
    updated_at: datetime
    participants: list[ParticipantRead]
    turn_selection: TurnSelectionConfigRead
    context: ContextConfigRead
    validation: ValidationConfigRead
    resolution: ResolutionConfigRead
