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


class ProposalConfigCreate(BaseModel):
    tools: list[str] = Field(
        title="Proposal tools",
        description="Tools available while participants write their initial proposals.",
    )


class ProposalConfigRead(BaseModel):
    tools: list[str]


class DebateConfigCreate(BaseModel):
    round_count: int = Field(
        ge=1,
        title="Debate rounds",
        description="Number of debate rounds to run after independent proposals.",
    )
    debaters: list[ParticipantCreate] = Field(
        min_length=1,
        title="Debaters",
        description="Agents who write proposals and take turns during the debate.",
    )
    turn_selection: TurnSelectionConfigCreate = Field(title="Turn selection")
    history: HistoryConfigCreate = Field(title="History")
    tools: list[str] = Field(
        title="Debate tools",
        description="Tools available while participants respond during debate rounds.",
    )


class DebateConfigRead(BaseModel):
    round_count: int
    debaters: list[ParticipantRead]
    turn_selection: TurnSelectionConfigRead
    history: HistoryConfigRead
    tools: list[str]


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
    proposal: ProposalConfigCreate
    debate: DebateConfigCreate
    resolution: ResolutionConfigCreate


class SessionConfigRead(BaseModel):
    id: UUID
    prompt: str
    seed: int
    created_at: datetime
    updated_at: datetime
    proposal: ProposalConfigRead
    debate: DebateConfigRead
    resolution: ResolutionConfigRead
