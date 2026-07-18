from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.session_configs.models.participants import JudgeParticipant
from api.modules.sessions.models.events import ResolutionCompletedEvent, ResolutionVoteEvent
from api.modules.strategies.resolution.adjudication import adjudication_messages, run_adjudication

JUDGE_SYSTEM_PROMPT = (
    "You are a neutral judge resolving a structured debate. "
    "Decide the strongest answer to the session prompt using only the transcript."
)


# TODO: Consider a way to optimize this instead of double generation. Avoid asking for verdict as a tool parameter because we need streaming.
class JudgeResolutionStrategy:
    def __init__(self, *, judge: JudgeParticipant) -> None:
        self._judge = judge

    async def resolve(self, ctx: EngineContext, *, generation_runner: GenerationRunner) -> EngineOutputStream:
        vote: ResolutionVoteEvent | None = None
        async for output in run_adjudication(
            ctx=ctx,
            adjudicator=self._judge,
            messages=adjudication_messages(
                ctx=ctx,
                adjudicator=self._judge,
                system_prompt=JUDGE_SYSTEM_PROMPT,
            ),
            generation_runner=generation_runner,
        ):
            if isinstance(output, ResolutionVoteEvent):
                vote = output
            yield output

        assert vote is not None

        winner = next(participant for participant in ctx.debaters if participant.id == vote.selected_participant_id)

        yield ResolutionCompletedEvent(
            session_id=ctx.session_id,
            decision=f"Selected {winner.name}.",
        )
