from api.modules.ai.models import AIMessage, GenerationOptions, MessageRole
from api.modules.engine.generation import GenerationRunner
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.session_configs.models.participants import DebaterParticipant
from api.modules.sessions.models.events import (
    Event,
    MessageStartedEvent,
    ProposalCompletedEvent,
    ProposalStartedEvent,
)
from api.modules.strategies.turn_selection.base import TurnSelectionStrategy
from api.shared.iterables import find_last_instance

PROPOSAL_ROUND_NUMBER = 0


class ProposalStage:
    def __init__(
        self,
        *,
        turn_selection_strategy: TurnSelectionStrategy,
        generation_runner: GenerationRunner,
    ) -> None:
        self._turn_selection_strategy = turn_selection_strategy
        self._generation_runner = generation_runner

    async def run(self, ctx: EngineContext) -> EngineOutputStream:
        if any(isinstance(event, ProposalCompletedEvent) for event in ctx.events):
            return

        if not any(isinstance(event, ProposalStartedEvent) for event in ctx.events):
            yield ProposalStartedEvent(session_id=ctx.session_id)
            return

        participant = _choose_next_participant(
            participants=self._turn_selection_strategy.order_participants(
                ctx,
                round_number=PROPOSAL_ROUND_NUMBER,
            ),
            events=ctx.events,
        )

        if not participant:
            yield ProposalCompletedEvent(session_id=ctx.session_id)
            return

        async for output in self._generation_runner.run_response(
            session_id=ctx.session_id,
            sender=participant,
            messages=_build_proposal_messages(ctx=ctx, participant=participant),
            options=GenerationOptions(
                model=participant.model,
                reasoning_effort=participant.reasoning_effort,
                temperature=participant.temperature,
            ),
        ):
            yield output


def _choose_next_participant(
    *, participants: list[DebaterParticipant], events: list[Event]
) -> DebaterParticipant | None:
    proposal_started = find_last_instance(events, ProposalStartedEvent)
    if proposal_started is None:
        return None

    proposal_started_index, _ = proposal_started
    completed_participant_ids = {
        event.sender_id for event in events[proposal_started_index + 1 :] if isinstance(event, MessageStartedEvent)
    }

    return next((participant for participant in participants if participant.id not in completed_participant_ids), None)


def _build_proposal_messages(
    *,
    ctx: EngineContext,
    participant: DebaterParticipant,
) -> list[AIMessage]:
    return [
        AIMessage(role=MessageRole.SYSTEM, content=participant.system_prompt),
        AIMessage(
            role=MessageRole.USER,
            content=(
                f"Session prompt:\n{ctx.prompt}\n\n"
                "Draft your independent initial proposal. Do not respond to other participants yet.\n\n"
                f"Respond as {participant.name}."
            ),
        ),
    ]
