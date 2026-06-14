from api.modules.ai.service import AIService
from api.modules.engine.models import EngineContext
from api.modules.engine.stages.base import EngineStage
from api.modules.engine.stages.debate import DebateStage
from api.modules.sessions.models.events import Event, SessionCompletedEvent, SessionStartedEvent
from api.modules.strategies.context.full import FullContextStrategy
from api.modules.strategies.turn_selection.round_robin import RoundRobinTurnSelectionStrategy


class Engine:
    def __init__(self, ai_service: AIService) -> None:
        self._stages: list[EngineStage] = [
            DebateStage(
                turn_selection_strategy=RoundRobinTurnSelectionStrategy(),
                context_strategy=FullContextStrategy(),
                ai_service=ai_service,
            ),
        ]

    async def step(self, ctx: EngineContext) -> list[Event]:
        if not any(isinstance(event, SessionStartedEvent) for event in ctx.events):
            return [SessionStartedEvent(session_id=ctx.session.id)]

        if any(isinstance(event, SessionCompletedEvent) for event in ctx.events):
            return []

        for stage in self._stages:
            events = await stage.run(ctx)
            if events:
                return events

        return []
