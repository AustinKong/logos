from collections.abc import AsyncIterable, Sequence
from typing import Any

from litellm import AsyncIterator, CustomStreamWrapper, ModelResponse, ModelResponseStream, acompletion
from litellm.types.utils import Delta, Message
from pydantic import ValidationError

from api.modules.ai.errors import AIProviderError
from api.modules.ai.models import (
    AIMessage,
    AIMessageDelta,
    AIMessageResponseAction,
    AIReasoningDelta,
    AIResponse,
    AIResponseEvent,
    GenerationOptions,
)
from api.modules.ai.providers.base import GeneratedObject


class LiteLLMProvider:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def generate_response(self, *, messages: Sequence[AIMessage], options: GenerationOptions) -> AIResponse:
        try:
            response = await acompletion(
                **_completion_kwargs(api_key=self._api_key, messages=messages, options=options)
            )
        except Exception as exc:
            raise AIProviderError() from exc

        message = _get_response_message(response)
        _raise_if_tool_calls(message)
        return AIResponse(
            reasoning=_get_reasoning_content(message),
            action=AIMessageResponseAction(content=_get_message_content(message)),
        )

    async def stream_response(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
    ) -> AsyncIterable[AIResponseEvent]:
        try:
            response = await acompletion(
                **_completion_kwargs(api_key=self._api_key, messages=messages, options=options),
                stream=True,
            )

            if isinstance(response, ModelResponse):
                raise AIProviderError("Expected streaming response from AI provider")

            async def gen() -> AsyncIterator[AIResponseEvent]:
                async for chunk in response:
                    delta = _get_stream_chunk_delta(chunk)
                    if delta is None:
                        continue

                    _raise_if_tool_calls(delta)
                    if reasoning_content := _get_reasoning_content(delta):
                        yield AIReasoningDelta(content=reasoning_content)

                    if content := delta.content:
                        yield AIMessageDelta(content=content)

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

        # Don't care about reasoning or tool calls for structured output
        content = _get_message_content(_get_response_message(response))
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
        "reasoning_effort": options.reasoning_effort.value,
    }
    if options.temperature is not None:
        kwargs["temperature"] = options.temperature
    if options.max_tokens is not None:
        kwargs["max_tokens"] = options.max_tokens
    return kwargs


def _get_response_message(response: ModelResponse | CustomStreamWrapper) -> Message:
    if isinstance(response, CustomStreamWrapper):
        raise AIProviderError("Expected non-streaming response from AI provider")
    return response.choices[0].message


def _get_message_content(message: Message) -> str:
    if message.content is None:
        raise AIProviderError("AI provider returned no text content")
    return message.content


def _get_stream_chunk_delta(chunk: ModelResponseStream) -> Delta | None:
    if not chunk.choices:
        return None
    return chunk.choices[0].delta


def _raise_if_tool_calls(source: Message | Delta) -> None:
    # TODO: Map LiteLLM tool calls to AIToolCallsResponseAction once app-level tools exist.
    if getattr(source, "tool_calls", None):
        raise AIProviderError("AI provider returned tool calls, but tool calls are not supported yet")
    if getattr(source, "function_call", None):
        raise AIProviderError("AI provider returned function calls, but tool calls are not supported yet")


def _get_reasoning_content(source: Message | Delta) -> str | None:
    """Return LiteLLM reasoning content, including Anthropic's thinking-block fallback.

    LiteLLM standardizes most providers into `reasoning_content`, but Anthropic can
    also return signed `thinking_blocks` that need to be preserved for later tool
    turns. See https://docs.litellm.ai/docs/reasoning_content.
    """
    if reasoning_content := getattr(source, "reasoning_content", None):
        return reasoning_content

    if thinking_blocks := getattr(source, "thinking_blocks", None):
        return "".join(block.get("thinking") or block.get("data") or "" for block in thinking_blocks) or None

    return None
