from collections.abc import Sequence

from api.modules.ai.models import AIMessage, MessageRole
from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.engine.timeline.debate_rounds import debate_rounds_from_events
from api.modules.engine.timeline.messages import InternalEventVisibility, TurnMessageMode, ai_messages_from_turns
from api.modules.engine.timeline.turns import next_participant, turns_from_events
from api.modules.session_configs.models.session_configs import DebateConfig
from api.modules.sessions.models.events import (
    AskUserStartedEvent,
    DebateRoundCompletedEvent,
    DebateRoundStartedEvent,
    MessageCompletedEvent,
    ProposalCompletedEvent,
    TurnCompletedEvent,
    TurnStartedEvent,
)
from api.modules.strategies.history.base import HistoryStrategy
from api.modules.strategies.turn_selection.base import TurnSelectionStrategy
from api.modules.tools.base import Tool

DEBATE_PROMPT = (
    "Session prompt:\n{prompt}\n\n"
    "Debate round: {round_number}\n\n"
    "Continue the conversation as {participant_name}. Do not restate the whole context or repeat ideas you agree "
    "with. Only write what you disagree with, what you think was missed, or what changed your mind. Respond "
    "directly to the previous points, naming other participants when useful."
)


class DebateStage:
    def __init__(
        self,
        *,
        config: DebateConfig,
        turn_selection_strategy: TurnSelectionStrategy,
        history_strategy: HistoryStrategy,
        generation_runner: GenerationRunner,
        tools: Sequence[Tool],
    ) -> None:
        self._config = config
        self._turn_selection_strategy = turn_selection_strategy
        self._history_strategy = history_strategy
        self._generation_runner = generation_runner
        self._tools = tools

    async def run(self, ctx: EngineContext) -> EngineOutputStream:
        if not any(isinstance(event, ProposalCompletedEvent) for event in ctx.events):
            return

        completed_rounds, open_round = debate_rounds_from_events(ctx.events)
        if open_round is None:
            if len(completed_rounds) >= self._config.round_count:
                return

            yield DebateRoundStartedEvent(
                session_id=ctx.session_id,
                round_number=len(completed_rounds) + 1,
            )
            return

        completed_turns, _ = turns_from_events(ctx.events)
        if open_round.open_turn is None:
            participant = next_participant(
                participants=self._turn_selection_strategy.order_participants(
                    ctx,
                    round_number=open_round.started.round_number,
                ),
                completed_turns=open_round.completed_turns,
            )

            if not participant:
                yield DebateRoundCompletedEvent(session_id=ctx.session_id)
                return

            yield TurnStartedEvent(session_id=ctx.session_id, sender_id=participant.id)
            return

        participant = next(
            (participant for participant in ctx.debaters if participant.id == open_round.open_turn.started.sender.id),
            None,
        )
        if participant is None:
            raise ValueError("Open agent turn has no debater participant")

        turn_completed = False
        async for output in self._generation_runner.run_response(
            session_id=ctx.session_id,
            sender=participant,
            messages=[
                AIMessage(role=MessageRole.SYSTEM, content=participant.system_prompt),
                AIMessage(
                    role=MessageRole.USER,
                    content=DEBATE_PROMPT.format(
                        prompt=ctx.prompt,
                        round_number=open_round.started.round_number,
                        participant_name=participant.name,
                    ),
                ),
                *ai_messages_from_turns(
                    self._history_strategy.select_turns(completed_turns),
                    mode=TurnMessageMode.HISTORY,
                    include_internal_events_from=InternalEventVisibility.NONE,
                ),
                *ai_messages_from_turns(
                    [open_round.open_turn],
                    mode=TurnMessageMode.CONTINUATION,
                    include_internal_events_from={participant.id},
                ),
            ],
            tools=self._tools,
        ):
            if isinstance(output, MessageCompletedEvent):
                turn_completed = True
            elif isinstance(output, AskUserStartedEvent):
                turn_completed = False
            yield output

        if turn_completed:
            yield TurnCompletedEvent(session_id=ctx.session_id)
