from collections.abc import Sequence

from api.modules.ai.models import AIMessage, MessageRole
from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.engine.timeline.messages import InternalEventVisibility, TurnMessageMode, ai_messages_from_turns
from api.modules.engine.timeline.turns import turns_from_events
from api.modules.session_configs.models.participants import JudgeParticipant, JurorParticipant
from api.modules.sessions.models.events import (
    MessageCompletedEvent,
    ResolutionVoteEvent,
    TurnCompletedEvent,
    TurnStartedEvent,
)
from api.modules.tools.resolution_vote.tool import ResolutionVoteTool

VOTE_PROMPT = (
    "Submit exactly one resolution vote matching the verdict above. "
    "Do not reconsider the verdict or send another message; use the provided tool."
)
VERDICT_PROMPT = """Session prompt:
{session_prompt}

Review the debate and give your verdict and reasoning as a concise message. Clearly name the winning participant."""


# TODO: For agents to vote themselves, we need to allow include internal events also.
def adjudication_messages(
    *,
    ctx: EngineContext,
    adjudicator: JudgeParticipant | JurorParticipant,
    system_prompt: str,
) -> list[AIMessage]:
    completed_turns, _ = turns_from_events(ctx.events)
    return [
        AIMessage(role=MessageRole.SYSTEM, content=f"{system_prompt}\n\n{adjudicator.system_prompt}"),
        *ai_messages_from_turns(
            completed_turns,
            mode=TurnMessageMode.HISTORY,
            include_internal_events_from=InternalEventVisibility.NONE,
        ),
        AIMessage(
            role=MessageRole.USER,
            content=VERDICT_PROMPT.format(session_prompt=ctx.prompt),
        ),
    ]


async def run_adjudication(
    *,
    ctx: EngineContext,
    adjudicator: JudgeParticipant | JurorParticipant,
    messages: Sequence[AIMessage],
    generation_runner: GenerationRunner,
) -> EngineOutputStream:
    yield TurnStartedEvent(session_id=ctx.session_id, sender_id=adjudicator.id)

    verdict: str | None = None
    async for output in generation_runner.run_response(
        session_id=ctx.session_id,
        sender=adjudicator,
        messages=messages,
        tools=[],
    ):
        if isinstance(output, MessageCompletedEvent):
            verdict = output.content
        yield output

    if verdict is None:
        raise RuntimeError("Adjudicator generation completed without a verdict")

    vote: ResolutionVoteEvent | None = None
    async for output in generation_runner.run_response(
        session_id=ctx.session_id,
        sender=adjudicator,
        messages=[
            *messages,
            AIMessage(role=MessageRole.ASSISTANT, content=verdict),
            AIMessage(role=MessageRole.USER, content=VOTE_PROMPT),
        ],
        tools=[ResolutionVoteTool(eligible_participants=ctx.debaters)],
    ):
        if isinstance(output, ResolutionVoteEvent):
            vote = output
        yield output

    # TODO: Consider retries on failure instead of error.
    if vote is None:
        raise RuntimeError("Adjudicator generation completed without a resolution vote")

    yield TurnCompletedEvent(session_id=ctx.session_id)
