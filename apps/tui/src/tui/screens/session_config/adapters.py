from api_client.models import SessionConfigCreate, SessionConfigRead, SessionCreate, SessionRead

from tui.screens.session_config.models import SessionConfigFormState
from tui.screens.session_config.sections.general.adapters import (
    general_create_from_form_state,
    general_form_state_from_read,
)
from tui.screens.session_config.sections.history.adapters import (
    history_create_from_form_state,
    history_form_state_from_read,
)
from tui.screens.session_config.sections.participants.adapters import (
    participants_create_from_form_state,
    participants_form_state_from_read,
)
from tui.screens.session_config.sections.resolution.adapters import (
    resolution_create_from_form_state,
    resolution_form_state_from_read,
)
from tui.screens.session_config.sections.turn_selection.adapters import (
    turn_selection_create_from_form_state,
    turn_selection_form_state_from_read,
)
from tui.screens.session_config.sections.validation.adapters import (
    validation_create_from_form_state,
    validation_form_state_from_read,
)


def form_state_from_config_read(config: SessionConfigRead, *, blank_seed: bool = False) -> SessionConfigFormState:
    # Preset configs read from the DB have a stored seed; blank it when using one as a create template.
    seed = "" if blank_seed else str(config.seed)
    return SessionConfigFormState(
        general=general_form_state_from_read(config.prompt, seed),
        participants=participants_form_state_from_read(config.participants),
        turn_selection=turn_selection_form_state_from_read(config.turn_selection),
        history=history_form_state_from_read(config.history),
        validation=validation_form_state_from_read(config.validation),
        resolution=resolution_form_state_from_read(config.resolution),
    )


def form_state_from_session_read(session: SessionRead) -> SessionConfigFormState:
    return form_state_from_config_read(session.config)


def session_create_from_form_state(form_state: SessionConfigFormState) -> SessionCreate:
    general = general_create_from_form_state(form_state.general)
    return SessionCreate(
        config=SessionConfigCreate(
            prompt=general.prompt,
            seed=general.seed,
            participants=participants_create_from_form_state(form_state.participants),
            turn_selection=turn_selection_create_from_form_state(form_state.turn_selection),
            history=history_create_from_form_state(form_state.history),
            validation=validation_create_from_form_state(form_state.validation),
            resolution=resolution_create_from_form_state(form_state.resolution),
        )
    )
