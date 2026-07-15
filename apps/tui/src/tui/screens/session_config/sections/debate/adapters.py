from api_client.models import DebateConfigCreate, DebateConfigRead
from tui.screens.session_config.errors import SessionConfigValidationError
from tui.screens.session_config.sections.debate.history.adapters import (
    history_create_from_form_state,
    history_form_state_from_read,
)
from tui.screens.session_config.sections.debate.models import DebateFormState
from tui.screens.session_config.sections.debate.turn_selection.adapters import (
    turn_selection_create_from_form_state,
    turn_selection_form_state_from_read,
)
from tui.screens.session_config.sections.participants.adapters import (
    participants_create_from_form_state,
    participants_form_state_from_read,
)


def debate_form_state_from_read(config: DebateConfigRead) -> DebateFormState:
    return DebateFormState(
        round_count=str(config.round_count),
        # FIXME:
        participants=participants_form_state_from_read(config.debaters),
        turn_selection=turn_selection_form_state_from_read(config.turn_selection),
        history=history_form_state_from_read(config.history),
        tools=config.tools,
    )


def debate_create_from_form_state(state: DebateFormState) -> DebateConfigCreate:
    return DebateConfigCreate(
        round_count=_round_count_create_from_form_state(state.round_count),
        debaters=participants_create_from_form_state(state.participants),
        turn_selection=turn_selection_create_from_form_state(state.turn_selection),
        history=history_create_from_form_state(state.history),
        tools=state.tools,
    )


def _round_count_create_from_form_state(round_count_value: str) -> int:
    try:
        round_count = int(round_count_value)
    except ValueError as exc:
        raise SessionConfigValidationError("Debate rounds must be a whole number") from exc

    if round_count < 1:
        raise SessionConfigValidationError("Debate rounds must be at least 1")

    return round_count
