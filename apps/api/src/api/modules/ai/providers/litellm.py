import json
from collections.abc import AsyncIterable, Sequence
from typing import Any

from litellm import AsyncIterator, CustomStreamWrapper, ModelResponse, ModelResponseStream, acompletion, aembedding
from litellm.types.utils import ChatCompletionDeltaToolCall, Delta, Message
from pydantic import ValidationError

from api.modules.ai.errors import AIProviderError
from api.modules.ai.models import (
    AIEmbedding,
    AIMessage,
    AIMessageDelta,
    AIMessageResponseAction,
    AIProviderName,
    AIReasoningDelta,
    AIResponse,
    AIResponseEvent,
    AIToolCall,
    AIToolCallEvent,
    AIToolCallsResponseAction,
    EmbeddingOptions,
    GenerationOptions,
    MessageRole,
    ReasoningEffort,
)
from api.modules.ai.prompts import response_prompt_instruction
from api.modules.ai.providers.base import GeneratedObject


class LiteLLMProvider:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def embed(self, *, text: str, options: EmbeddingOptions) -> AIEmbedding:
        try:
            response = await aembedding(
                model=options.model,
                input=text,
                api_key=self._api_key,
                drop_params=True,
            )
        except Exception as exc:
            raise AIProviderError() from exc

        return response.data[0].embedding

    async def generate_response(self, *, messages: Sequence[AIMessage], options: GenerationOptions) -> AIResponse:
        try:
            response = await acompletion(
                **_completion_kwargs(api_key=self._api_key, messages=messages, options=options)
            )
        except Exception as exc:
            raise AIProviderError() from exc

        message = _get_response_message(response)
        if tool_calls := _get_tool_calls(message):
            return AIResponse(
                reasoning=_get_reasoning_content(message),
                action=AIToolCallsResponseAction(tool_calls=tool_calls),
            )

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
        """Stream response events with tool calls normalized to the end of the turn.

        LiteLLM can stream function arguments as partial tool-call chunks. This
        provider buffers those chunks until the stream is exhausted and only then emits
        AIToolCallEvent values. Callers therefore receive forwarded reasoning/message
        deltas before tool calls, with tool calls ordered by provider tool-call index.
        """
        try:
            response = await acompletion(
                **_completion_kwargs(api_key=self._api_key, messages=messages, options=options),
                stream=True,
            )

            if isinstance(response, ModelResponse):
                raise AIProviderError("Expected streaming response from AI provider")

            async def gen() -> AsyncIterator[AIResponseEvent]:
                tool_call_chunks: list[ChatCompletionDeltaToolCall] = []
                async for chunk in response:
                    delta = _get_stream_chunk_delta(chunk)
                    if delta is None:
                        continue

                    # Tool calls are streamed as chunks, assemble them before parsing
                    if delta.tool_calls:
                        tool_call_chunks.extend(delta.tool_calls)
                        continue

                    if reasoning_content := _get_reasoning_content(delta):
                        yield AIReasoningDelta(content=reasoning_content)

                    if content := delta.content:
                        yield AIMessageDelta(content=content)

                for tool_call in _tool_calls_from_chunks(tool_call_chunks):
                    yield AIToolCallEvent(tool_call=tool_call)

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
                **_completion_kwargs(
                    api_key=self._api_key,
                    messages=messages,
                    options=options,
                    apply_verbosity=False,
                ),
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


def _completion_kwargs(
    *,
    api_key: str,
    messages: Sequence[AIMessage],
    options: GenerationOptions,
    apply_verbosity: bool = True,
) -> dict[str, Any]:
    effective_messages = _messages_with_verbosity_instruction(messages, options) if apply_verbosity else messages
    litellm_messages = [{"role": message.role.value, "content": message.content} for message in effective_messages]

    kwargs: dict[str, Any] = {
        "model": _litellm_model_for_options(options),
        "messages": litellm_messages,
        "api_key": api_key,
        "drop_params": True,
    }
    # Models that do not support reasoning can reject even `reasoning_effort="none"` (from LiteLLM.)
    if options.reasoning_effort is not ReasoningEffort.NONE:
        kwargs["reasoning_effort"] = {"effort": options.reasoning_effort.value, "summary": "detailed"}
    if apply_verbosity:
        kwargs["text"] = {"verbosity": options.verbosity.value}
    if options.temperature is not None:
        kwargs["temperature"] = options.temperature
    if options.max_tokens is not None:
        kwargs["max_tokens"] = options.max_tokens
    if options.tools:
        kwargs["tools"] = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in options.tools
        ]
    return kwargs


def _messages_with_verbosity_instruction(
    messages: Sequence[AIMessage],
    options: GenerationOptions,
) -> list[AIMessage]:
    """Prepend a system message with the verbosity instruction to the messages list."""
    instruction = response_prompt_instruction(options.verbosity)
    if not messages:
        return [AIMessage(role=MessageRole.SYSTEM, content=instruction)]

    first_message, *remaining_messages = messages
    if first_message.role is MessageRole.SYSTEM:
        return [
            AIMessage(
                role=MessageRole.SYSTEM,
                content=f"{instruction}\n\n{first_message.content}",
            ),
            *remaining_messages,
        ]

    return [
        AIMessage(role=MessageRole.SYSTEM, content=instruction),
        *messages,
    ]


def _litellm_model_for_options(options: GenerationOptions) -> str:
    provider, _, model = options.model.partition("/")
    if provider == AIProviderName.OPENAI.value and model:
        # LiteLLM currently needs OpenAI reasoning/verbosity requests routed
        # through its Responses API bridge. Keep this provider routing detail
        # out of persisted/catalog model IDs.
        # Reference: https://github.com/BerriAI/litellm/issues/17428
        return "/".join((provider, "responses", model))

    return options.model


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


def _get_tool_calls(message: Message) -> list[AIToolCall]:
    tool_calls = []
    for tool_call in message.tool_calls or []:
        if not tool_call.function.name:
            raise AIProviderError("AI provider returned a tool call without a function name")
        tool_calls.append(_parse_tool_call(tool_call.function.name, tool_call.function.arguments))

    return tool_calls


def _tool_calls_from_chunks(chunks: Sequence[ChatCompletionDeltaToolCall]) -> list[AIToolCall]:
    parts_by_index: dict[int, tuple[list[str], list[str]]] = {}
    for chunk in chunks:
        name_parts, argument_parts = parts_by_index.setdefault(chunk.index, ([], []))
        if chunk.function.name:
            name_parts.append(chunk.function.name)
        if chunk.function.arguments:
            argument_parts.append(chunk.function.arguments)

    tool_calls: list[AIToolCall] = []
    for index in sorted(parts_by_index):
        name_parts, argument_parts = parts_by_index[index]
        tool_calls.append(_parse_tool_call("".join(name_parts), "".join(argument_parts)))

    return tool_calls


def _parse_tool_call(name: str, arguments_str: str) -> AIToolCall:
    if not name:
        raise AIProviderError("AI provider returned a tool call without a function name")

    arguments = {}
    if arguments_str:
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError as exc:
            raise AIProviderError("AI provider returned invalid tool call JSON arguments") from exc

    return AIToolCall(
        name=name,
        arguments=arguments,
    )


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

    # OpenAI can emit post-hoc summaries as `reasoning_items` after already
    # streaming the same observable reasoning through `reasoning_content`.
    # Ignore them to avoid duplicating the reasoning stream at the end.
    return None
