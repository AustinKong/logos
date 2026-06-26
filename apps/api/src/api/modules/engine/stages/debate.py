from uuid import uuid4

from api.modules.ai.models import GenerationOptions
from api.modules.ai.service import AIService
from api.modules.engine.models import EngineContext, EngineOutputStream, Token
from api.modules.session_configs.models.participants import AgentParticipant
from api.modules.sessions.models.events import MessageCompletedEvent, MessageStartedEvent
from api.modules.strategies.context.base import ContextStrategy
from api.modules.strategies.turn_selection.base import TurnSelectionStrategy


class DebateStage:
    def __init__(
        self,
        *,
        turn_selection_strategy: TurnSelectionStrategy,
        context_strategy: ContextStrategy,
        ai_service: AIService,
    ) -> None:
        self._turn_selection_strategy = turn_selection_strategy
        self._context_strategy = context_strategy
        self._ai_service = ai_service

    async def run(self, ctx: EngineContext) -> EngineOutputStream:
        selected_participant = self._turn_selection_strategy.choose_participant(ctx)
        if selected_participant is None:
            return
        if not isinstance(selected_participant, AgentParticipant):
            # TODO: Add human/system turn handling when those participant types become eligible.
            return

        agent = selected_participant
        message_id = uuid4()
        token_stream = await self._ai_service.stream_text(
            messages=self._context_strategy.build_messages(ctx, agent),
            options=GenerationOptions(model=agent.model),
        )

        yield MessageStartedEvent(
            session_id=ctx.session.id,
            message_id=message_id,
            sender_id=agent.id,
        )

        content_parts: list[str] = []
        async for token_content in token_stream:
            content_parts.append(token_content)
            yield Token(correlation_id=message_id, content=token_content)

        # TODO: Add option to think without creating a message in future
        yield MessageCompletedEvent(
            session_id=ctx.session.id,
            message_id=message_id,
            content="".join(content_parts),
        )
