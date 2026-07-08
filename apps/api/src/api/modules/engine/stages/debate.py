from api.modules.ai.models import AIMessage, GenerationOptions, MessageRole
from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.session_configs.models.participants import DebaterParticipant
from api.modules.sessions.models.events import (
    DebateRoundCompletedEvent,
    DebateRoundStartedEvent,
    Event,
    MessageStartedEvent,
    ProposalCompletedEvent,
)
from api.modules.strategies.history.base import HistoryStrategy
from api.modules.strategies.turn_selection.base import TurnSelectionStrategy
from api.shared.iterables import find_last_instance


class DebateStage:
    def __init__(
        self,
        *,
        debate_round_count: int,
        turn_selection_strategy: TurnSelectionStrategy,
        history_strategy: HistoryStrategy,
        generation_runner: GenerationRunner,
    ) -> None:
        self._debate_round_count = debate_round_count
        self._turn_selection_strategy = turn_selection_strategy
        self._history_strategy = history_strategy
        self._generation_runner = generation_runner

    async def run(self, ctx: EngineContext) -> EngineOutputStream:
        if not any(isinstance(event, ProposalCompletedEvent) for event in ctx.events):
            return

        active_round = _get_active_round(ctx.events)
        if active_round is None:
            completed_round_count = sum(isinstance(event, DebateRoundCompletedEvent) for event in ctx.events)
            if completed_round_count >= self._debate_round_count:
                return

            yield DebateRoundStartedEvent(
                session_id=ctx.session_id,
                round_number=completed_round_count + 1,
            )
            return

        active_round_index, active_round_started = active_round

        participant = _choose_next_participant(
            participants=self._turn_selection_strategy.order_participants(
                ctx,
                round_number=active_round_started.round_number,
            ),
            events=ctx.events,
            active_round_index=active_round_index,
        )

        if not participant:
            yield DebateRoundCompletedEvent(session_id=ctx.session_id)
            return

        async for output in self._generation_runner.run_response(
            session_id=ctx.session_id,
            sender=participant,
            messages=_build_debate_messages(
                ctx=ctx,
                participant=participant,
                round_number=active_round_started.round_number,
                history=self._history_strategy.build_history(ctx),
            ),
            options=GenerationOptions(
                model=participant.model,
                reasoning_effort=participant.reasoning_effort,
                verbosity=participant.verbosity,
                temperature=participant.temperature,
            ),
        ):
            yield output


def _get_active_round(events: list[Event]) -> tuple[int, DebateRoundStartedEvent] | None:
    """Returns the index and event of the most recent DebateRoundStartedEvent that has not yet been completed."""
    round_marker = find_last_instance(events, (DebateRoundStartedEvent, DebateRoundCompletedEvent))
    if round_marker is None:
        return None

    index, event = round_marker
    if isinstance(event, DebateRoundStartedEvent):
        return index, event

    return None


def _choose_next_participant(
    *,
    participants: list[DebaterParticipant],
    events: list[Event],
    active_round_index: int,
) -> DebaterParticipant | None:
    completed_participant_ids = {
        event.sender_id for event in events[active_round_index + 1 :] if isinstance(event, MessageStartedEvent)
    }

    return next((participant for participant in participants if participant.id not in completed_participant_ids), None)


def _build_debate_messages(
    *,
    ctx: EngineContext,
    participant: DebaterParticipant,
    round_number: int,
    history: str | None,
) -> list[AIMessage]:
    return [
        AIMessage(role=MessageRole.SYSTEM, content=participant.system_prompt),
        AIMessage(
            role=MessageRole.USER,
            content=(
                f"Session prompt:\n{ctx.prompt}\n\n"
                f"Debate round: {round_number}\n\n"
                f"Transcript so far:\n{history or '(none)'}\n\n"
                f"Continue the conversation as {participant.name}. Assume everyone already has the session prompt "
                "and transcript. Do not restate the whole context or repeat ideas you agree with. Only write what "
                "you disagree with, what you think was missed, or what changed your mind. Respond directly to the "
                "previous points, naming other participants when useful."
            ),
        ),
    ]
