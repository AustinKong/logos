from typing import assert_never

from api_client.models import (
    RoundRobinTurnSelectionConfigCreate,
    RoundRobinTurnSelectionConfigRead,
    ShuffledTurnSelectionConfigCreate,
    ShuffledTurnSelectionConfigRead,
    TurnSelectionConfigCreate,
    TurnSelectionConfigRead,
)

from tui.screens.session_config.sections.turn_selection.models import (
    RoundRobinTurnSelectionFormState,
    ShuffledTurnSelectionFormState,
    TurnSelectionFormState,
)


def turn_selection_form_state_from_read(config: TurnSelectionConfigRead) -> TurnSelectionFormState:
    match config:
        case RoundRobinTurnSelectionConfigRead():
            return RoundRobinTurnSelectionFormState()
        case ShuffledTurnSelectionConfigRead():
            return ShuffledTurnSelectionFormState()
        case _ as never:
            assert_never(never)


def turn_selection_create_from_form_state(state: TurnSelectionFormState) -> TurnSelectionConfigCreate:
    match state:
        case RoundRobinTurnSelectionFormState():
            return RoundRobinTurnSelectionConfigCreate()
        case ShuffledTurnSelectionFormState():
            return ShuffledTurnSelectionConfigCreate()
        case _ as never:
            assert_never(never)
