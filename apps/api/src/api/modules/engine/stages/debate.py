from api.modules.ai.models import GenerationOptions
from api.modules.ai.service import AIService
from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import Event, ParticipantMessageEvent
from api.modules.sessions.models.participants import AgentParticipant
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

    async def run(self, ctx: EngineContext) -> list[Event]:
        selected_participant = self._turn_selection_strategy.choose_participant(ctx)
        if selected_participant is None:
            return []
        if not isinstance(selected_participant, AgentParticipant):
            # TODO: Add human/system turn handling when those participant types become eligible.
            return []

        agent = selected_participant
        content = await self._ai_service.generate_text(
            messages=self._context_strategy.build_messages(ctx, agent),
            options=GenerationOptions(model=agent.model),
        )
        # TODO: Add option to think without creating a message in future
        return [
            ParticipantMessageEvent(
                session_id=ctx.session.id,
                sender_id=agent.id,
                content=content,
            )
        ]
