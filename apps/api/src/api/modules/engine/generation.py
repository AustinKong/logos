from collections.abc import Sequence
from typing import assert_never
from uuid import UUID, uuid4

from api.modules.ai.errors import AIProviderError
from api.modules.ai.models import (
    AIMessage,
    AIMessageDelta,
    AIReasoningDelta,
    AIToolCall,
    AIToolCallEvent,
    GenerationOptions,
)
from api.modules.ai.service import AIService
from api.modules.engine.models import EngineOutputStream, Token
from api.modules.session_configs.models.participants import Participant
from api.modules.sessions.models.events import (
    MessageCompletedEvent,
    MessageStartedEvent,
    ReasoningCompletedEvent,
    ReasoningStartedEvent,
    TurnCompletedEvent,
)
from api.modules.tools.adapters import ai_tool_definition_from_definition
from api.modules.tools.base import Tool, ToolExecutionContext


class GenerationRunner:
    def __init__(self, *, ai_service: AIService) -> None:
        self._ai_service = ai_service

    # TODO: May need to split into run_response based on judge/jury requirements.
    # This fn right now auto appends TurnCompletedEvent which doesn't work with judge/jury
    async def run_turn(
        self,
        *,
        session_id: UUID,
        sender: Participant,
        messages: Sequence[AIMessage],
        tools: Sequence[Tool],
    ) -> EngineOutputStream:
        tools_by_name = {tool.definition.name: tool for tool in tools}
        response_stream = await self._ai_service.stream_response(
            messages=messages,
            options=GenerationOptions(
                model=sender.model,
                tools=[ai_tool_definition_from_definition(tool.definition) for tool in tools],
                temperature=sender.temperature,
                reasoning_effort=sender.reasoning_effort,
                verbosity=sender.verbosity,
            ),
        )

        reasoning_started_event_id, message_started_event_id = uuid4(), uuid4()
        reasoning_open = message_started = False
        reasoning_parts: list[str] = []
        message_parts: list[str] = []
        tool_calls: list[AIToolCall] = []

        def build_reasoning_completed() -> ReasoningCompletedEvent:
            return ReasoningCompletedEvent(
                session_id=session_id,
                started_event_id=reasoning_started_event_id,
                content="".join(reasoning_parts),
            )

        async for response_event in response_stream:
            match response_event:
                case AIReasoningDelta():
                    if message_started or tool_calls:
                        raise AIProviderError("AI provider returned reasoning after action content")

                    if not reasoning_open:
                        reasoning_open = True
                        yield ReasoningStartedEvent(
                            id=reasoning_started_event_id,
                            session_id=session_id,
                        )

                    reasoning_parts.append(response_event.content)
                    yield Token(stream_id=reasoning_started_event_id, content=response_event.content)
                case AIMessageDelta():
                    if tool_calls:
                        raise AIProviderError("AI provider returned message content after a tool call")

                    if reasoning_open:
                        reasoning_open = False
                        yield build_reasoning_completed()

                    if not message_started:
                        message_started = True
                        yield MessageStartedEvent(
                            id=message_started_event_id,
                            session_id=session_id,
                        )

                    message_parts.append(response_event.content)
                    yield Token(stream_id=message_started_event_id, content=response_event.content)
                case AIToolCallEvent():
                    tool_calls.append(response_event.tool_call)
                case _ as never:
                    assert_never(never)

        if reasoning_open:
            yield build_reasoning_completed()

        if not message_started and not tool_calls:
            raise AIProviderError("AI provider returned no action")

        if message_started:
            yield MessageCompletedEvent(
                session_id=session_id,
                started_event_id=message_started_event_id,
                content="".join(message_parts),
            )

        for tool_call in tool_calls:
            try:
                handler: Tool = tools_by_name[tool_call.name]
            except KeyError as exc:
                raise AIProviderError(f"AI provider requested an unavailable tool: {tool_call.name}") from exc

            for event in await handler.execute(
                tool_call=tool_call,
                ctx=ToolExecutionContext(session_id=session_id, sender=sender),
            ):
                yield event

        # A tool call keeps the turn open so the agent can consume its result.
        if message_started and not tool_calls:
            yield TurnCompletedEvent(session_id=session_id)
