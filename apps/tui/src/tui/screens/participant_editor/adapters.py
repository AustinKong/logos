from api_client.models import (
    ParticipantCreate,
    ParticipantRead,
)
from textual.widgets import Select

from tui.screens.participant_editor.models import ParticipantFormState, ParticipantsFormState
from tui.screens.session_config.errors import SessionConfigValidationError


def participants_form_state_from_read(participants: list[ParticipantRead]) -> ParticipantsFormState:
    return ParticipantsFormState(
        participants=[participant_form_state_from_read(participant) for participant in participants],
    )


def participants_create_from_form_state(state: ParticipantsFormState) -> list[ParticipantCreate]:
    return [
        participant_create_from_form_state(
            participant,
            participant_label="Debater",
        )
        for participant in state.participants
    ]


def participant_form_state_from_read(participant: ParticipantRead) -> ParticipantFormState:
    return ParticipantFormState(
        name=participant.name,
        model=participant.model,
        reasoning_effort=participant.reasoning_effort,
        verbosity=participant.verbosity,
        temperature=str(participant.temperature),
        system_prompt=participant.system_prompt,
    )


def participant_create_from_form_state(
    participant: ParticipantFormState,
    *,
    participant_label: str,
) -> ParticipantCreate:
    if not participant.name.strip():
        raise SessionConfigValidationError(f"{participant_label} name is required")
    if participant.model == Select.NULL or not str(participant.model):
        raise SessionConfigValidationError(f"{participant_label} model is required")
    if not participant.system_prompt.strip():
        raise SessionConfigValidationError(f"{participant_label} system prompt is required")

    try:
        temperature = float(participant.temperature)
    except ValueError as exc:
        raise SessionConfigValidationError(f"{participant_label} temperature must be a number") from exc

    return ParticipantCreate(
        name=participant.name,
        model=str(participant.model),
        reasoning_effort=participant.reasoning_effort,
        verbosity=participant.verbosity,
        temperature=temperature,
        system_prompt=participant.system_prompt,
    )
