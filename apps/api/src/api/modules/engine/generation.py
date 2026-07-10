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
)
from api.modules.tools.base import ToolExecutionContext
from api.modules.tools.resolver import ToolResolver


# TODO: Kinda messy rn, will see if i can simplify abit
class GenerationRunner:
    def __init__(self, *, ai_service: AIService, tool_resolver: ToolResolver) -> None:
        self._ai_service = ai_service
        self._tool_resolver = tool_resolver

    async def run_response(
        self,
        *,
        session_id: UUID,
        sender: Participant,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
    ) -> EngineOutputStream:
        response_stream = await self._ai_service.stream_response(
            messages=messages,
            options=GenerationOptions(
                model=options.model,
                # TODO: Remove list definitions. Not all models should have the same definitions.
                tools=self._tool_resolver.list_definitions(),
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
                            sender_id=sender.id,
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
                            sender_id=sender.id,
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
                    handler = self._tool_resolver.resolve(response_event.tool_call.name)
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
