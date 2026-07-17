from collections.abc import Sequence
from typing import assert_never
from uuid import UUID, uuid4

from api.modules.ai.errors import AIProviderError
from api.modules.ai.models import (
    AIMessage,
    AIMessageDelta,
    AIReasoningDelta,
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


# TODO: Kinda messy rn, will see if i can simplify abit
class GenerationRunner:
    def __init__(self, *, ai_service: AIService) -> None:
        self._ai_service = ai_service

    async def run_response(
        self,
        *,
        session_id: UUID,
        sender: Participant,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
        tools: Sequence[Tool],
    ) -> EngineOutputStream:
        tools_by_name = {tool.definition.name: tool for tool in tools}
        response_stream = await self._ai_service.stream_response(
            messages=messages,
            options=GenerationOptions(
                model=options.model,
                tools=[ai_tool_definition_from_definition(tool.definition) for tool in tools],
                temperature=options.temperature,
                max_tokens=options.max_tokens,
                reasoning_effort=options.reasoning_effort,
                verbosity=options.verbosity,
            ),
        )

        reasoning_id, message_id = uuid4(), uuid4()
        reasoning_started = reasoning_completed = action_started = False
        tool_action_started = False
        reasoning_parts: list[str] = []
        message_parts: list[str] = []

        def build_reasoning_completed() -> ReasoningCompletedEvent:
            return ReasoningCompletedEvent(
                session_id=session_id,
                reasoning_id=reasoning_id,
                content="".join(reasoning_parts),
            )

        async for response_event in response_stream:
            match response_event:
                case AIReasoningDelta():
                    if action_started:
                        raise AIProviderError("AI provider returned reasoning after action content")

                    if not reasoning_started:
                        reasoning_started = True
                        yield ReasoningStartedEvent(
                            session_id=session_id,
                            reasoning_id=reasoning_id,
                        )

                    reasoning_parts.append(response_event.content)
                    yield Token(correlation_id=reasoning_id, content=response_event.content)
                case AIMessageDelta():
                    if reasoning_started and not reasoning_completed:
                        reasoning_completed = True
                        yield build_reasoning_completed()

                    if not action_started:
                        action_started = True
                        yield MessageStartedEvent(
                            session_id=session_id,
                            message_id=message_id,
                        )

                    message_parts.append(response_event.content)
                    yield Token(correlation_id=message_id, content=response_event.content)
                case AIToolCallEvent():
                    # AI providers must emit tool calls only after all reasoning/message deltas
                    # for the turn, so the runner handles tool events in arrival order.
                    if action_started:
                        raise AIProviderError("AI provider returned tool call after message content")

                    if reasoning_started and not reasoning_completed:
                        reasoning_completed = True
                        yield build_reasoning_completed()

                    tool_action_started = True
                    try:
                        handler: Tool = tools_by_name[response_event.tool_call.name]
                    except KeyError as exc:
                        raise AIProviderError(
                            f"AI provider requested an unavailable tool: {response_event.tool_call.name}"
                        ) from exc
                    for event in await handler.execute(
                        tool_call=response_event.tool_call,
                        ctx=ToolExecutionContext(session_id=session_id, sender=sender),
                    ):
                        yield event
                case _ as never:
                    assert_never(never)

        if tool_action_started:
            return

        if reasoning_started and not reasoning_completed:
            yield build_reasoning_completed()

        if not action_started:
            raise AIProviderError("AI provider returned no message content")

        yield MessageCompletedEvent(
            session_id=session_id,
            message_id=message_id,
            content="".join(message_parts),
        )

    async def run_turn(
        self,
        *,
        session_id: UUID,
        sender: Participant,
        messages: Sequence[AIMessage],
        tools: Sequence[Tool],
    ) -> EngineOutputStream:
        completed = False
        async for output in self.run_response(
            session_id=session_id,
            sender=sender,
            messages=messages,
            tools=tools,
            options=GenerationOptions(
                model=sender.model,
                reasoning_effort=sender.reasoning_effort,
                verbosity=sender.verbosity,
                temperature=sender.temperature,
            ),
        ):
            if isinstance(output, MessageCompletedEvent):
                completed = True
            yield output

        # TODO: Message completion may not be the only way to complete a turn.
        if completed:
            yield TurnCompletedEvent(session_id=session_id)
