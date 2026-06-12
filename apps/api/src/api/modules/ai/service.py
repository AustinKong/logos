from collections.abc import AsyncIterable, Sequence
from typing import TypeVar

from pydantic import BaseModel

from api.modules.ai.models import AIMessage, GenerationOptions
from api.modules.ai.resolver import AIProviderResolver

GeneratedObject = TypeVar("GeneratedObject", bound=BaseModel)


class AIService:
    def __init__(self, provider_resolver: AIProviderResolver) -> None:
        self._provider_resolver = provider_resolver

    async def generate_text(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
    ) -> str:
        provider = self._provider_resolver.resolve(options.model)
        return await provider.generate_text(messages=messages, options=options)

    async def stream_text(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
    ) -> AsyncIterable[str]:
        provider = self._provider_resolver.resolve(options.model)
        return await provider.stream_text(messages=messages, options=options)

    async def generate_object(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
        response_model: type[GeneratedObject],
    ) -> GeneratedObject:
        provider = self._provider_resolver.resolve(options.model)
        return await provider.generate_object(messages=messages, options=options, response_model=response_model)
