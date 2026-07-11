from pydantic import BaseModel

from api.modules.ai.models import AIProviderName


class AILanguageModelRead(BaseModel):
    id: str
    label: str
    provider: AIProviderName
    supports_reasoning: bool


class AIEmbeddingModelRead(BaseModel):
    id: str
    label: str
    provider: AIProviderName
