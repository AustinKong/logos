from api_client.models import (
    AgentParticipantRead,
    AIModelRead,
    JudgeResolutionConfigRead,
    SessionConfigCreate,
    SessionConfigRead,
    SessionCreate,
    SessionRead,
)

from tui.screens.session_config.models import ModelOptionState, SessionConfigFormState
from tui.screens.session_config.sections.context.adapters import (
    context_create_from_form_state,
    context_form_state_from_read,
)
from tui.screens.session_config.sections.participants.adapters import (
    participants_create_from_form_state,
    participants_form_state_from_read,
)
from tui.screens.session_config.sections.prompt.adapters import (
    prompt_create_from_form_state,
    prompt_form_state_from_read,
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


def form_state_from_config_read(config: SessionConfigRead) -> SessionConfigFormState:
    return SessionConfigFormState(
        prompt=prompt_form_state_from_read(config.prompt),
        participants=participants_form_state_from_read(config.participants),
        turn_selection=turn_selection_form_state_from_read(config.turn_selection),
        context=context_form_state_from_read(config.context),
        validation=validation_form_state_from_read(config.validation),
        resolution=resolution_form_state_from_read(config.resolution),
    )


def form_state_from_session_read(session: SessionRead) -> SessionConfigFormState:
    return form_state_from_config_read(session.config)


def model_options_from_ai_models(models: list[AIModelRead]) -> list[ModelOptionState]:
    return [ModelOptionState(id=model.id, label=model.label) for model in models]


def model_options_from_config_read(config: SessionConfigRead) -> list[ModelOptionState]:
    model_ids = {
        participant.model for participant in config.participants if isinstance(participant, AgentParticipantRead)
    }
    if isinstance(config.resolution, JudgeResolutionConfigRead):
        model_ids.add(config.resolution.judge_model)

    return [ModelOptionState(id=model_id, label=model_id) for model_id in sorted(model_ids)]


def session_create_from_form_state(form_state: SessionConfigFormState) -> SessionCreate:
    return SessionCreate(
        config=SessionConfigCreate(
            prompt=prompt_create_from_form_state(form_state.prompt),
            participants=participants_create_from_form_state(form_state.participants),
            turn_selection=turn_selection_create_from_form_state(form_state.turn_selection),
            context=context_create_from_form_state(form_state.context),
            validation=validation_create_from_form_state(form_state.validation),
            resolution=resolution_create_from_form_state(form_state.resolution),
        )
    )
