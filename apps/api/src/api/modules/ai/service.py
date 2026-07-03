from collections.abc import AsyncIterable, Sequence
from typing import TypeVar

from pydantic import BaseModel

from api.modules.ai.models import AIMessage, AIModel, AIResponse, AIResponseEvent, GenerationOptions
from api.modules.ai.resolver import AIProviderResolver

GeneratedObject = TypeVar("GeneratedObject", bound=BaseModel)


class AIService:
    def __init__(self, provider_resolver: AIProviderResolver) -> None:
        self._provider_resolver = provider_resolver

    async def generate_response(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
    ) -> AIResponse:
        provider = self._provider_resolver.resolve(options.model)
        return await provider.generate_response(messages=messages, options=options)

    async def stream_response(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
    ) -> AsyncIterable[AIResponseEvent]:
        provider = self._provider_resolver.resolve(options.model)
        return await provider.stream_response(messages=messages, options=options)

    async def generate_object(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
        response_model: type[GeneratedObject],
    ) -> GeneratedObject:
        provider = self._provider_resolver.resolve(options.model)
        return await provider.generate_object(messages=messages, options=options, response_model=response_model)

    def list_available_models(self) -> list[AIModel]:
        return self._provider_resolver.list_available_models()
