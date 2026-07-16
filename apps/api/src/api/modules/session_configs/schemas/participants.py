from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.ai.models import ReasoningEffort, Verbosity
from api.modules.session_configs.models.participants import ParticipantType


class ParticipantCreate(BaseModel):
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
    reasoning_effort: ReasoningEffort = Field(
        title="Reasoning effort",
        description="Model reasoning effort used for this participant's responses.",
    )
    verbosity: Verbosity = Field(
        title="Verbosity",
        description="Output verbosity used for this participant's responses.",
    )
    temperature: float = Field(
        title="Temperature",
        description="Sampling temperature used for this participant's responses.",
    )


class ParticipantRead(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    model: str
    system_prompt: str
    reasoning_effort: ReasoningEffort
    verbosity: Verbosity
    temperature: float
    type: ParticipantType = Field(
        title="Role",
        description="Role this participant has in the session.",
    )
