from collections.abc import AsyncIterable, Sequence
from typing import Protocol, TypeVar

from pydantic import BaseModel

from api.modules.ai.models import (
    AIEmbedding,
    AIEmbeddingModel,
    AILanguageModel,
    AIMessage,
    AIResponse,
    AIResponseEvent,
    EmbeddingOptions,
    GenerationOptions,
)

# Bind to BaseModel because we use model_validate_json
GeneratedObject = TypeVar("GeneratedObject", bound=BaseModel)


class AIProvider(Protocol):
    def list_language_models(self) -> list[AILanguageModel]: ...

    def list_embedding_models(self) -> list[AIEmbeddingModel]: ...

    async def embed(self, *, text: str, options: EmbeddingOptions) -> AIEmbedding: ...

    async def generate_response(self, *, messages: Sequence[AIMessage], options: GenerationOptions) -> AIResponse: ...

    async def stream_response(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
    ) -> AsyncIterable[AIResponseEvent]: ...

    async def generate_object(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
        response_model: type[GeneratedObject],
    ) -> GeneratedObject: ...
