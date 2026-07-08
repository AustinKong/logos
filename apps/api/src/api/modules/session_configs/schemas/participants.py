from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from api.modules.ai.models import ReasoningEffort, Verbosity
from api.modules.session_configs.models.participants import ParticipantType


class ParticipantCreateBase(BaseModel):
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


class ParticipantReadBase(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    model: str
    system_prompt: str
    reasoning_effort: ReasoningEffort
    verbosity: Verbosity
    temperature: float


class DebaterParticipantCreate(ParticipantCreateBase):
    pass


class JudgeParticipantCreate(ParticipantCreateBase):
    pass


class JurorParticipantCreate(ParticipantCreateBase):
    pass


class DebaterParticipantRead(ParticipantReadBase):
    type: Literal[ParticipantType.DEBATER] = Field(
        ParticipantType.DEBATER,
        title="Debater",
        description="Participant that proposes and debates responses.",
    )


class JudgeParticipantRead(ParticipantReadBase):
    type: Literal[ParticipantType.JUDGE] = Field(
        ParticipantType.JUDGE,
        title="Judge",
        description="Participant that resolves the debate as a neutral judge.",
    )


class JurorParticipantRead(ParticipantReadBase):
    type: Literal[ParticipantType.JUROR] = Field(
        ParticipantType.JUROR,
        title="Juror",
        description="Participant that contributes one vote in a jury resolution.",
    )


type ParticipantRead = Annotated[
    DebaterParticipantRead | JudgeParticipantRead | JurorParticipantRead,
    Field(discriminator="type"),
]
