from pydantic import BaseModel

from api.modules.ai.models import AIProviderName


class AIModelRead(BaseModel):
    id: str
    label: str
    provider: AIProviderName
