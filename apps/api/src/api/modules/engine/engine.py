from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.engine.stages.base import EngineStage
from api.modules.engine.stages.debate import DebateStage
from api.modules.engine.stages.proposal import ProposalStage
from api.modules.engine.stages.resolution import ResolutionStage
from api.modules.sessions.models.events import SessionCompletedEvent, SessionStartedEvent
from api.modules.sessions.models.sessions import Session
from api.modules.strategies.resolver import StrategyResolver


class Engine:
    def __init__(
        self,
        *,
        generation_runner: GenerationRunner,
        strategy_resolver: StrategyResolver,
    ) -> None:
        self._generation_runner = generation_runner
        self._strategy_resolver = strategy_resolver

    def _build_stages(self, session: Session) -> list[EngineStage]:
        turn_selection_strategy = self._strategy_resolver.turn_selection(session)

        return [
            ProposalStage(
                turn_selection_strategy=turn_selection_strategy,
                generation_runner=self._generation_runner,
            ),
            DebateStage(
                debate_round_count=session.config.debate_round_count,
                turn_selection_strategy=turn_selection_strategy,
                history_strategy=self._strategy_resolver.history(session),
                generation_runner=self._generation_runner,
            ),
            ResolutionStage(
                resolution_strategy=self._strategy_resolver.resolution(session),
            ),
        ]

    async def step(self, session: Session, ctx: EngineContext) -> EngineOutputStream:
        if not any(isinstance(event, SessionStartedEvent) for event in ctx.events):
            yield SessionStartedEvent(session_id=ctx.session_id)
            return

        if any(isinstance(event, SessionCompletedEvent) for event in ctx.events):
            return

        for stage in self._build_stages(session):
            has_output = False
            async for output in stage.run(ctx):
                has_output = True
                yield output

            # Only run one stage per step
            if has_output:
                return
