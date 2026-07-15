from collections.abc import Sequence

from api.modules.ai.models import AIMessage, MessageRole
from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.engine.timeline.messages import TurnMessageMode, ai_messages_from_turns
from api.modules.engine.timeline.turns import next_participant, turns_from_events
from api.modules.session_configs.models.configs import ProposalConfig
from api.modules.sessions.models.events import (
    ProposalCompletedEvent,
    ProposalStartedEvent,
    TurnStartedEvent,
)
from api.modules.strategies.turn_selection.base import TurnSelectionStrategy
from api.modules.tools.base import Tool

PROPOSAL_ROUND_NUMBER = 0
PROPOSAL_PROMPT = (
    "Session prompt:\n{prompt}\n\n"
    "Draft your independent initial proposal. Do not respond to other participants yet. Write it like the opening "
    "turn in a working conversation, not a formal report.\n\n"
    "Respond as {participant_name}."
)


class ProposalStage:
    def __init__(
        self,
        *,
        config: ProposalConfig,
        turn_selection_strategy: TurnSelectionStrategy,
        generation_runner: GenerationRunner,
        tools: Sequence[Tool],
    ) -> None:
        self._config = config
        self._turn_selection_strategy = turn_selection_strategy
        self._generation_runner = generation_runner
        self._tools = tools

    async def run(self, ctx: EngineContext) -> EngineOutputStream:
        if any(isinstance(event, ProposalCompletedEvent) for event in ctx.events):
            return

        if not any(isinstance(event, ProposalStartedEvent) for event in ctx.events):
            yield ProposalStartedEvent(session_id=ctx.session_id)
            return

        completed_turns, open_turn = turns_from_events(ctx.events)
        if open_turn is None:
            participant = next_participant(
                participants=self._turn_selection_strategy.order_participants(
                    ctx,
                    round_number=PROPOSAL_ROUND_NUMBER,
                ),
                completed_turns=completed_turns,
            )

            if not participant:
                yield ProposalCompletedEvent(session_id=ctx.session_id)
                return

            yield TurnStartedEvent(session_id=ctx.session_id, sender_id=participant.id)
            return

        participant = next(
            (participant for participant in ctx.debaters if participant.id == open_turn.started.sender.id),
            None,
        )
        if participant is None:
            raise ValueError("Open agent turn has no debater participant")

        async for output in self._generation_runner.run_turn(
            session_id=ctx.session_id,
            sender=participant,
            messages=[
                AIMessage(role=MessageRole.SYSTEM, content=participant.system_prompt),
                AIMessage(
                    role=MessageRole.USER,
                    content=PROPOSAL_PROMPT.format(
                        prompt=ctx.prompt,
                        participant_name=participant.name,
                    ),
                ),
                *ai_messages_from_turns(
                    [open_turn],
                    mode=TurnMessageMode.CONTINUATION,
                    include_internal_events_from={participant.id},
                ),
            ],
            tools=self._tools,
        ):
            yield output
