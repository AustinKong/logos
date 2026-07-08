from typing import assert_never

from api_client.models import (
    DebaterParticipantCreate,
    DebaterParticipantRead,
    ParticipantRead,
)
from textual.widgets import Select

from tui.screens.session_config.errors import SessionConfigValidationError
from tui.screens.session_config.sections.participants.models import (
    ParticipantFormState,
    ParticipantsFormState,
)


def participants_form_state_from_read(participants: list[ParticipantRead]) -> ParticipantsFormState:
    return ParticipantsFormState(
        participants=[participant_form_state_from_read(participant) for participant in participants],
    )


def participants_create_from_form_state(state: ParticipantsFormState) -> list[DebaterParticipantCreate]:
    return [participant_create_from_form_state(participant) for participant in state.participants]


def participant_form_state_from_read(participant: ParticipantRead) -> ParticipantFormState:
    match participant:
        case DebaterParticipantRead():
            return ParticipantFormState(
                name=participant.name,
                model=participant.model,
                reasoning_effort=participant.reasoning_effort,
                verbosity=participant.verbosity,
                temperature=str(participant.temperature),
                system_prompt=participant.system_prompt,
            )
        case _ as never:
            # TODO: Shouldnt assert never
            assert_never(never)


def participant_create_from_form_state(participant: ParticipantFormState) -> DebaterParticipantCreate:
    match participant:
        case ParticipantFormState():
            if not participant.name.strip():
                raise SessionConfigValidationError("Participant name is required")
            if participant.model == Select.NULL or not str(participant.model):
                raise SessionConfigValidationError("Participant model is required")
            model = str(participant.model)
            if not participant.system_prompt.strip():
                raise SessionConfigValidationError("Participant system prompt is required")

            try:
                temperature = float(participant.temperature)
            except ValueError as exc:
                raise SessionConfigValidationError("Participant temperature must be a number") from exc

            return DebaterParticipantCreate(
                name=participant.name,
                model=model,
                reasoning_effort=participant.reasoning_effort,
                verbosity=participant.verbosity,
                temperature=temperature,
                system_prompt=participant.system_prompt,
            )
        case _ as never:
            assert_never(never)
