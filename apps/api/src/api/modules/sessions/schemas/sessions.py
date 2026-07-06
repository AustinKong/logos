from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from api.modules.session_configs.schemas.session_configs import SessionConfigCreate, SessionConfigRead
from api.modules.sessions.models.sessions import SessionStatus


class SessionCreate(BaseModel):
    config: SessionConfigCreate


class SessionRead(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    config: SessionConfigRead


class SessionSummaryRead(BaseModel):
    id: UUID
    prompt: str
    created_at: datetime
    updated_at: datetime
    participant_count: int
    status: SessionStatus


class SessionExportResponse(BaseModel):
    path: str
