from collections.abc import AsyncIterable, Sequence
from typing import Any

from litellm import AsyncIterator, CustomStreamWrapper, ModelResponse, ModelResponseStream, acompletion
from pydantic import ValidationError

from api.modules.ai.errors import AIProviderError
from api.modules.ai.models import AIMessage, GenerationOptions
from api.modules.ai.providers.base import GeneratedObject


class LiteLLMProvider:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def generate_text(self, *, messages: Sequence[AIMessage], options: GenerationOptions) -> str:
        try:
            response = await acompletion(
                **_completion_kwargs(api_key=self._api_key, messages=messages, options=options)
            )
        except Exception as exc:
            raise AIProviderError() from exc

        return _get_response_content(response)

    async def stream_text(self, *, messages: Sequence[AIMessage], options: GenerationOptions) -> AsyncIterable[str]:
        try:
            response = await acompletion(
                **_completion_kwargs(api_key=self._api_key, messages=messages, options=options),
                stream=True,
            )

            if isinstance(response, ModelResponse):
                raise AIProviderError("Expected streaming response from AI provider")

            async def gen() -> AsyncIterator[str]:
                async for chunk in response:
                    content = _get_stream_chunk_content(chunk)
                    if content:
                        yield content

            return gen()
        except Exception as exc:
            raise AIProviderError() from exc

    async def generate_object(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
        response_model: type[GeneratedObject],
    ) -> GeneratedObject:
        try:
            response = await acompletion(
                **_completion_kwargs(api_key=self._api_key, messages=messages, options=options),
                response_format=response_model,
            )
        except Exception as exc:
            raise AIProviderError() from exc

        content = _get_response_content(response)
        try:
            return response_model.model_validate_json(content)
        except ValidationError as exc:
            raise AIProviderError("AI provider returned invalid structured output") from exc


def _completion_kwargs(*, api_key: str, messages: Sequence[AIMessage], options: GenerationOptions) -> dict[str, Any]:
    litellm_messages = [{"role": message.role.value, "content": message.content} for message in messages]
    kwargs: dict[str, Any] = {
        "model": options.model,
        "messages": litellm_messages,
        "api_key": api_key,
    }
    if options.temperature is not None:
        kwargs["temperature"] = options.temperature
    if options.max_tokens is not None:
        kwargs["max_tokens"] = options.max_tokens
    return kwargs


def _get_response_content(response: ModelResponse | CustomStreamWrapper) -> str:
    if isinstance(response, CustomStreamWrapper):
        raise AIProviderError("Expected non-streaming response from AI provider")

    choices = getattr(response, "choices", None)
    if not choices:
        raise AIProviderError("AI provider returned no choices")

    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None)
    if not isinstance(content, str):
        raise AIProviderError("AI provider returned no text content")

    return content


def _get_stream_chunk_content(chunk: ModelResponseStream) -> str | None:
    choices = getattr(chunk, "choices", None)
    if not choices:
        return None

    delta = getattr(choices[0], "delta", None)
    content = getattr(delta, "content", None)
    if content is None:
        return None
    if not isinstance(content, str):
        raise AIProviderError("AI provider returned non-text stream content")

    return content
