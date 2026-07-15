from pydantic import BaseModel


class ToolRead(BaseModel):
    name: str
    title: str
    description: str
