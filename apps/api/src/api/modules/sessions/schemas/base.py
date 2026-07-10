from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# This lives outside events.py to avoid a circular import:
# sessions.schemas.events imports tool event schemas for the EventRead union,
# while tool event schemas need the shared event read fields below.
# TODO: Reconsider file placement and schema ownership. Circular imports shouldn't happen for a well-designed structure.
class EventReadBase(BaseModel):
    id: UUID
    session_id: UUID
    created_at: datetime
    updated_at: datetime
