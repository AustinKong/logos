from api_client.models import ValidationConfigCreate, ValidationConfigRead

from tui.screens.session_config.sections.validation.models import ValidationFormState


def validation_form_state_from_read(config: ValidationConfigRead) -> ValidationFormState:
    return config


def validation_create_from_form_state(state: ValidationFormState) -> ValidationConfigCreate:
    return ValidationConfigCreate(mode=state.mode)
