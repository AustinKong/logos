from collections.abc import AsyncIterable, Sequence
from typing import TypeVar

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
from api.modules.ai.resolver import AIProviderResolver
from api.settings import Settings

GeneratedObject = TypeVar("GeneratedObject", bound=BaseModel)


class AIService:
    def __init__(self, *, provider_resolver: AIProviderResolver, settings: Settings) -> None:
        self._provider_resolver = provider_resolver
        self._settings = settings

    async def embed(
        self,
        *,
        text: str,
        options: EmbeddingOptions | None = None,
    ) -> AIEmbedding:
        options = options or EmbeddingOptions(model=self._settings.ai.embedding_model)
        provider = self._provider_resolver.resolve_embedding_model(options.model)
        return await provider.embed(text=text, options=options)

    async def generate_response(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
    ) -> AIResponse:
        provider = self._provider_resolver.resolve_language_model(options.model)
        return await provider.generate_response(messages=messages, options=options)

    async def stream_response(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
    ) -> AsyncIterable[AIResponseEvent]:
        provider = self._provider_resolver.resolve_language_model(options.model)
        return await provider.stream_response(messages=messages, options=options)

    async def generate_object(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
        response_model: type[GeneratedObject],
    ) -> GeneratedObject:
        provider = self._provider_resolver.resolve_language_model(options.model)
        return await provider.generate_object(messages=messages, options=options, response_model=response_model)

    def list_available_language_models(self) -> list[AILanguageModel]:
        return self._provider_resolver.list_available_language_models()

    def list_available_embedding_models(self) -> list[AIEmbeddingModel]:
        return self._provider_resolver.list_available_embedding_models()
