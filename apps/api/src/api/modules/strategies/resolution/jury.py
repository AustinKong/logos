from collections import Counter

from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.session_configs.models.participants import JurorParticipant
from api.modules.sessions.models.events import ResolutionCompletedEvent, ResolutionVoteEvent
from api.modules.strategies.resolution.adjudication import adjudication_messages, run_adjudication

JURY_SYSTEM_PROMPT = (
    "You are an impartial juror resolving a structured debate. "
    "Independently decide the strongest answer to the session prompt using only the transcript."
)


# TODO: No tiebreaker right now. Its just first write wins right now.
class JuryResolutionStrategy:
    def __init__(
        self,
        *,
        jurors: list[JurorParticipant],
    ) -> None:
        self._jurors = jurors

    async def resolve(self, ctx: EngineContext, *, generation_runner: GenerationRunner) -> EngineOutputStream:
        if not self._jurors:
            raise RuntimeError("Jury resolution requires at least one juror")

        votes: list[ResolutionVoteEvent] = []

        for juror in self._jurors:
            async for output in run_adjudication(
                ctx=ctx,
                adjudicator=juror,
                messages=adjudication_messages(
                    ctx=ctx,
                    adjudicator=juror,
                    system_prompt=JURY_SYSTEM_PROMPT,
                ),
                generation_runner=generation_runner,
            ):
                if isinstance(output, ResolutionVoteEvent):
                    votes.append(output)
                yield output

        vote_counts = Counter(vote.selected_participant_id for vote in votes)
        winner = max(ctx.debaters, key=lambda participant: vote_counts[participant.id])
        yield ResolutionCompletedEvent(
            session_id=ctx.session_id,
            decision=f"Selected {winner.name}.",
        )
