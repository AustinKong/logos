from uuid import UUID

from pydantic import BaseModel


class TokenRead(BaseModel):
    correlation_id: UUID
    content: str
