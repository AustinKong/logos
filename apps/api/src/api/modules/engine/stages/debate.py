from api.modules.ai.models import AIMessage, GenerationOptions, MessageRole
from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.session_configs.models.participants import AgentParticipant, UserParticipant
from api.modules.strategies.history.base import HistoryStrategy
from api.modules.strategies.turn_selection.base import TurnSelectionStrategy


class DebateStage:
    def __init__(
        self,
        *,
        turn_selection_strategy: TurnSelectionStrategy,
        history_strategy: HistoryStrategy,
        generation_runner: GenerationRunner,
    ) -> None:
        self._turn_selection_strategy = turn_selection_strategy
        self._history_strategy = history_strategy
        self._generation_runner = generation_runner

    async def run(self, ctx: EngineContext) -> EngineOutputStream:
        participant = self._turn_selection_strategy.choose_participant(ctx)

        match participant:
            case AgentParticipant():
                async for output in self._generation_runner.run_response(
                    session_id=ctx.session_id,
                    sender=participant,
                    messages=_build_debate_messages(
                        ctx=ctx,
                        agent=participant,
                        history=self._history_strategy.build_history(ctx),
                    ),
                    options=GenerationOptions(
                        model=participant.model,
                        reasoning_effort=participant.reasoning_effort,
                    ),
                ):
                    yield output
            case UserParticipant():
                # TODO: Add human/system turn handling when those participant types become eligible.
                return
            case _:
                raise ValueError(f"Unsupported participant type: {participant.type}")


def _build_debate_messages(
    *,
    ctx: EngineContext,
    agent: AgentParticipant,
    history: str | None,
) -> list[AIMessage]:
    return [
        AIMessage(role=MessageRole.SYSTEM, content=agent.system_prompt),
        AIMessage(
            role=MessageRole.USER,
            content=(
                f"Session prompt:\n{ctx.prompt}\n\n"
                f"Transcript so far:\n{history or '(none)'}\n\n"
                f"Respond as {agent.name}."
            ),
        ),
    ]
