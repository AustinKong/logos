from uuid import UUID

from pydantic import BaseModel


class TokenRead(BaseModel):
    stream_id: UUID
    content: str
