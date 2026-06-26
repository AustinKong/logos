from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from api.modules.sessions.models.participants import ParticipantType


class AgentParticipantCreate(BaseModel):
    name: str
    model: str
    system_prompt: str


class ParticipantRead(BaseModel):
    id: UUID
    type: ParticipantType
    name: str
    created_at: datetime
    updated_at: datetime
