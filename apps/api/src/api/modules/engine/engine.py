from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.engine.stages.base import EngineStage
from api.modules.engine.stages.debate import DebateStage
from api.modules.engine.stages.resolution import ResolutionStage
from api.modules.engine.stages.validation import ValidationStage
from api.modules.sessions.models.events import SessionCompletedEvent, SessionStartedEvent
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

    def _build_stages(self, ctx: EngineContext) -> list[EngineStage]:
        return [
            DebateStage(
                turn_selection_strategy=self._strategy_resolver.turn_selection(ctx.session),
                history_strategy=self._strategy_resolver.history(ctx.session),
                generation_runner=self._generation_runner,
            ),
            ValidationStage(
                validation_strategy=self._strategy_resolver.validation(ctx.session),
            ),
            ResolutionStage(
                resolution_strategy=self._strategy_resolver.resolution(ctx.session),
            ),
        ]

    async def step(self, ctx: EngineContext) -> EngineOutputStream:
        if not any(isinstance(event, SessionStartedEvent) for event in ctx.events):
            yield SessionStartedEvent(session_id=ctx.session.id)
            return

        if any(isinstance(event, SessionCompletedEvent) for event in ctx.events):
            return

        for stage in self._build_stages(ctx):
            has_output = False
            async for output in stage.run(ctx):
                has_output = True
                yield output

            # Only run one stage per step
            if has_output:
                return
