from api_client.models import TurnSelectionConfigCreate, TurnSelectionConfigRead

from tui.screens.session_config.sections.turn_selection.state import TurnSelectionFormState


def turn_selection_form_state_from_read(config: TurnSelectionConfigRead) -> TurnSelectionFormState:
    return config


def turn_selection_create_from_form_state(state: TurnSelectionFormState) -> TurnSelectionConfigCreate:
    return TurnSelectionConfigCreate(mode=state.mode)
