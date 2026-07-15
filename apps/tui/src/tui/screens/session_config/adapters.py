from api_client.models import SessionConfigCreate, SessionConfigRead, SessionCreate, SessionRead

from tui.screens.session_config.models import SessionConfigFormState
from tui.screens.session_config.sections.debate.adapters import (
    debate_create_from_form_state,
    debate_form_state_from_read,
)
from tui.screens.session_config.sections.general.adapters import (
    general_create_from_form_state,
    general_form_state_from_read,
)
from tui.screens.session_config.sections.proposal.adapters import (
    proposal_create_from_form_state,
    proposal_form_state_from_read,
)
from tui.screens.session_config.sections.resolution.adapters import (
    resolution_create_from_form_state,
    resolution_form_state_from_read,
)


def form_state_from_config_read(config: SessionConfigRead, *, blank_seed: bool = False) -> SessionConfigFormState:
    # Preset configs read from the DB have a stored seed; blank it when using one as a create template.
    seed = "" if blank_seed else str(config.seed)
    return SessionConfigFormState(
        general=general_form_state_from_read(config.prompt, seed),
        proposal=proposal_form_state_from_read(config.proposal),
        debate=debate_form_state_from_read(config.debate),
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
            proposal=proposal_create_from_form_state(form_state.proposal),
            debate=debate_create_from_form_state(form_state.debate),
            resolution=resolution_create_from_form_state(form_state.resolution),
        )
    )
