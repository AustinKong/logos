from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.session_configs.schemas.configs import (
    HistoryConfigCreate,
    HistoryConfigRead,
    ResolutionConfigCreate,
    ResolutionConfigRead,
    TurnSelectionConfigCreate,
    TurnSelectionConfigRead,
    ValidationConfigCreate,
    ValidationConfigRead,
)
from api.modules.session_configs.schemas.participants import ParticipantCreate, ParticipantRead


class SessionConfigCreate(BaseModel):
    prompt: str = Field(
        min_length=1,
        title="Session prompt",
        description="Prompt that defines the session topic and instructions for participants.",
    )
    participants: list[ParticipantCreate] = Field(min_length=1)
    turn_selection: TurnSelectionConfigCreate
    history: HistoryConfigCreate
    validation: ValidationConfigCreate
    resolution: ResolutionConfigCreate


class SessionConfigRead(BaseModel):
    id: UUID
    prompt: str
    created_at: datetime
    updated_at: datetime
    participants: list[ParticipantRead]
    turn_selection: TurnSelectionConfigRead
    history: HistoryConfigRead
    validation: ValidationConfigRead
    resolution: ResolutionConfigRead
