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
)
from api.modules.session_configs.schemas.participants import ParticipantCreate, ParticipantRead


class SessionConfigCreate(BaseModel):
    prompt: str = Field(
        min_length=1,
        title="Session prompt",
        description="Prompt that defines the session topic and instructions for participants.",
    )
    seed: int | None = Field(
        title="Seed",
        description="Optional deterministic seed for random app behavior. Leave blank to generate one.",
    )
    debate_round_count: int = Field(
        ge=1,
        title="Debate rounds",
        description="Number of debate rounds to run after independent proposals.",
    )
    participants: list[ParticipantCreate] = Field(min_length=1)
    turn_selection: TurnSelectionConfigCreate
    history: HistoryConfigCreate
    resolution: ResolutionConfigCreate


class SessionConfigRead(BaseModel):
    id: UUID
    prompt: str
    seed: int
    debate_round_count: int
    created_at: datetime
    updated_at: datetime
    participants: list[ParticipantRead]
    turn_selection: TurnSelectionConfigRead
    history: HistoryConfigRead
    resolution: ResolutionConfigRead
