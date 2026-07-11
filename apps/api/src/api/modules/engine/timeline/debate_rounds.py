from dataclasses import dataclass

from api.modules.engine.timeline.turns import Turn, turns_from_events
from api.modules.sessions.models.events import DebateRoundCompletedEvent, DebateRoundStartedEvent, Event


@dataclass(slots=True)
class DebateRound:
    started: DebateRoundStartedEvent
    completed_turns: list[Turn]
    open_turn: Turn | None


def debate_rounds_from_events(events: list[Event]) -> tuple[list[DebateRound], DebateRound | None]:
    """
    Groups events into debate rounds based on DebateRoundStartedEvent and DebateRoundCompletedEvent.
    Returns a tuple of completed debate rounds and an open debate round (if any).
    Filters out any events that are not part of a debate round's turns.
    """
    completed: list[DebateRound] = []
    open_started_event: DebateRoundStartedEvent | None = None
    open_events: list[Event] = []

    for event in events:
        match event:
            case DebateRoundStartedEvent():
                open_started_event = event
                open_events = []
            case DebateRoundCompletedEvent():
                if open_started_event is not None:
                    completed_turns, open_turn = turns_from_events(open_events)
                    completed.append(
                        DebateRound(
                            started=open_started_event,
                            completed_turns=completed_turns,
                            open_turn=open_turn,
                        )
                    )
                    open_started_event = None
                    open_events = []
            case _:
                if open_started_event is not None:
                    open_events.append(event)

    if open_started_event is None:
        return completed, None

    completed_turns, open_turn = turns_from_events(open_events)
    return completed, DebateRound(
        started=open_started_event,
        completed_turns=completed_turns,
        open_turn=open_turn,
    )
