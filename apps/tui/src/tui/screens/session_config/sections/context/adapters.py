from api_client.models import ContextConfigCreate, ContextConfigRead

from tui.screens.session_config.sections.context.state import ContextFormState


def context_form_state_from_read(config: ContextConfigRead) -> ContextFormState:
    return config


def context_create_from_form_state(state: ContextFormState) -> ContextConfigCreate:
    return ContextConfigCreate(mode=state.mode)
