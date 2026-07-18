from collections.abc import Collection, Sequence
from enum import StrEnum
from typing import assert_never
from uuid import UUID

from api.modules.ai.models import AIMessage, MessageRole
from api.modules.engine.timeline.turns import Turn
from api.modules.sessions.models.events import (
    AskUserCompletedEvent,
    MessageCompletedEvent,
    ReasoningCompletedEvent,
)


class TurnMessageMode(StrEnum):
    HISTORY = "history"  # Gives messages "user" role so AI knows they are not from current turn
    CONTINUATION = "continuation"  # Gives messages "assistant" role so AI knows they are from current turn


# Internal events such as reasoning and tool calls should only be available to the agent themselves.
class InternalEventVisibility(StrEnum):
    ALL = "all"
    NONE = "none"


type InternalEventSources = Collection[UUID] | InternalEventVisibility


def ai_messages_from_turns(
    turns: Sequence[Turn],
    *,
    mode: TurnMessageMode,
    include_internal_events_from: InternalEventSources,
) -> list[AIMessage]:
    return [
        message
        for turn in turns
        for message in ai_message_from_turn(
            turn,
            mode=mode,
            include_internal_events_from=include_internal_events_from,
        )
    ]


def ai_message_from_turn(
    turn: Turn,
    *,
    mode: TurnMessageMode,
    include_internal_events_from: InternalEventSources,
) -> list[AIMessage]:
    messages: list[AIMessage] = []
    includes_internal_events = _includes_internal_events(
        turn,
        include_internal_events_from=include_internal_events_from,
    )

    for event in turn.events:
        match event:
            case ReasoningCompletedEvent() if includes_internal_events:
                if mode is TurnMessageMode.HISTORY:
                    messages.append(
                        AIMessage(
                            role=MessageRole.USER,
                            content=f"{turn.started.sender.name} reasoning:\n{event.content}",
                        )
                    )
                else:
                    messages.append(
                        AIMessage(
                            role=MessageRole.ASSISTANT,
                            content=f"Reasoning:\n{event.content}",
                        )
                    )
            case MessageCompletedEvent():
                if mode is TurnMessageMode.HISTORY:
                    messages.append(
                        AIMessage(
                            role=MessageRole.USER,
                            content=f"{turn.started.sender.name}: {event.content}",
                        )
                    )
                else:
                    messages.append(AIMessage(role=MessageRole.ASSISTANT, content=event.content))
            case AskUserCompletedEvent() if includes_internal_events:
                if mode is TurnMessageMode.HISTORY:
                    messages.append(
                        AIMessage(
                            role=MessageRole.USER,
                            content=(
                                f"{turn.started.sender.name} asked the user: {event.started_event.question}\n"
                                f"User answered: {event.answer}"
                            ),
                        )
                    )
                else:
                    messages.extend(
                        (
                            AIMessage(
                                role=MessageRole.ASSISTANT,
                                content=f"Asked the user: {event.started_event.question}",
                            ),
                            AIMessage(role=MessageRole.USER, content=f"User answered: {event.answer}"),
                        )
                    )
            case _:
                pass

    return messages


def _includes_internal_events(
    turn: Turn,
    *,
    include_internal_events_from: InternalEventSources,
) -> bool:
    if not isinstance(include_internal_events_from, InternalEventVisibility):
        return turn.started.sender_id in include_internal_events_from

    match include_internal_events_from:
        case InternalEventVisibility.ALL:
            return True
        case InternalEventVisibility.NONE:
            return False
        case _ as never:
            assert_never(never)
