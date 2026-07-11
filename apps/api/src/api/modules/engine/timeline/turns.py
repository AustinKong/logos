from collections.abc import Sequence
from dataclasses import dataclass

from api.modules.session_configs.models.participants import Participant
from api.modules.sessions.models.events import (
    Event,
    TurnCompletedEvent,
    TurnStartedEvent,
)


@dataclass(slots=True)
class Turn:
    started: TurnStartedEvent
    events: list[Event]


def turns_from_events(events: list[Event]) -> tuple[list[Turn], Turn | None]:
    """
    Groups events into turns based on TurnStartedEvent and TurnCompletedEvent.
    Returns a tuple of completed turns and an open turn (if any).
    Filters out any events that are not part of a turn.
    """
    completed: list[Turn] = []
    open_turn: Turn | None = None

    for event in events:
        match event:
            case TurnStartedEvent():
                open_turn = Turn(started=event, events=[])
            case TurnCompletedEvent():
                if open_turn is not None:
                    completed.append(open_turn)
                    open_turn = None
            case _:
                if open_turn is not None:
                    open_turn.events.append(event)

    return completed, open_turn


def next_participant(
    *,
    participants: Sequence[Participant],
    completed_turns: Sequence[Turn],
) -> Participant | None:
    """Given an ordered list of participants and a list of completed turns, returns the next participant who has not yet taken a turn."""
    completed_participant_ids = {turn.started.sender_id for turn in completed_turns}
    return next((participant for participant in participants if participant.id not in completed_participant_ids), None)
