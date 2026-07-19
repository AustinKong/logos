from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.engine.stages.base import EngineStage
from api.modules.engine.stages.debate import DebateStage
from api.modules.engine.stages.proposal import ProposalStage
from api.modules.engine.stages.resolution import ResolutionStage
from api.modules.sessions.models.sessions import Session
from api.modules.strategies.resolver import StrategyResolver
from api.modules.tools.models import ToolScope
from api.modules.tools.service import ToolService


class Engine:
    def __init__(
        self,
        *,
        generation_runner: GenerationRunner,
        strategy_resolver: StrategyResolver,
        tool_service: ToolService,
    ) -> None:
        self._generation_runner = generation_runner
        self._strategy_resolver = strategy_resolver
        self._tool_service = tool_service

    def _build_stages(self, session: Session) -> list[EngineStage]:
        debate_config = session.config.debate_config
        proposal_config = session.config.proposal_config
        turn_selection_strategy = self._strategy_resolver.turn_selection(session)

        return [
            ProposalStage(
                config=proposal_config,
                turn_selection_strategy=turn_selection_strategy,
                generation_runner=self._generation_runner,
                tools=self._tool_service.resolve_tools(proposal_config.tools, scope=ToolScope.PROPOSAL),
            ),
            DebateStage(
                config=debate_config,
                turn_selection_strategy=turn_selection_strategy,
                history_strategy=self._strategy_resolver.history(session),
                generation_runner=self._generation_runner,
                tools=self._tool_service.resolve_tools(debate_config.tools, scope=ToolScope.DEBATE),
            ),
            ResolutionStage(
                resolution_strategy=self._strategy_resolver.resolution(session),
                generation_runner=self._generation_runner,
            ),
        ]

    async def step(self, session: Session, ctx: EngineContext) -> EngineOutputStream:
        for stage in self._build_stages(session):
            has_output = False
            async for output in stage.run(ctx):
                has_output = True
                yield output

            # Only run one stage per step
            if has_output:
                return
