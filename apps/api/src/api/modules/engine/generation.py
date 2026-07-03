from collections.abc import Sequence
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
from api.modules.session_configs.models.participants import AgentParticipant
from api.modules.sessions.models.events import (
    MessageCompletedEvent,
    MessageStartedEvent,
    ReasoningCompletedEvent,
    ReasoningStartedEvent,
)


class GenerationRunner:
    def __init__(self, *, ai_service: AIService) -> None:
        self._ai_service = ai_service

    async def run_response(
        self,
        *,
        session_id: UUID,
        sender: AgentParticipant,  # TODO: Or judge participant, or jury participant in future. anything but user participant
        messages: Sequence[AIMessage],
        options: GenerationOptions,
    ) -> EngineOutputStream:
        response_stream = await self._ai_service.stream_response(messages=messages, options=options)

        reasoning_id, message_id = uuid4(), uuid4()
        reasoning_started = reasoning_completed = action_started = False
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
                    raise AIProviderError("Tool call responses are not supported yet")

        if reasoning_started and not reasoning_completed:
            yield build_reasoning_completed()

        if not action_started:
            # TODO: In the future with tool calls, no message content is valid
            raise AIProviderError("AI provider returned no message content")

        yield MessageCompletedEvent(
            session_id=session_id,
            message_id=message_id,
            content="".join(message_parts),
        )
