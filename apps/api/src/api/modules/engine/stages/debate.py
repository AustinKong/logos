from api.modules.ai.models import GenerationOptions
from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.session_configs.models.participants import AgentParticipant, UserParticipant
from api.modules.strategies.context.base import ContextStrategy
from api.modules.strategies.turn_selection.base import TurnSelectionStrategy


class DebateStage:
    def __init__(
        self,
        *,
        turn_selection_strategy: TurnSelectionStrategy,
        context_strategy: ContextStrategy,
        generation_runner: GenerationRunner,
    ) -> None:
        self._turn_selection_strategy = turn_selection_strategy
        self._context_strategy = context_strategy
        self._generation_runner = generation_runner

    async def run(self, ctx: EngineContext) -> EngineOutputStream:
        participant = self._turn_selection_strategy.choose_participant(ctx)

        match participant:
            case AgentParticipant():
                async for output in self._generation_runner.run_response(
                    session_id=ctx.session.id,
                    sender=participant,
                    messages=self._context_strategy.build_messages(ctx, participant),
                    options=GenerationOptions(
                        model=participant.model,
                        reasoning_effort=participant.reasoning_effort,
                    ),
                ):
                    yield output
            case UserParticipant():
                # TODO: Add human/system turn handling when those participant types become eligible.
                return
