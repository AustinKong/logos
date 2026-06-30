from enum import StrEnum

from attrs import define

from tui.screens.session_config.sections.context.state import ContextFormState
from tui.screens.session_config.sections.participants.state import ParticipantsFormState
from tui.screens.session_config.sections.prompt.state import PromptFormState
from tui.screens.session_config.sections.resolution.state import ResolutionFormState
from tui.screens.session_config.sections.turn_selection.state import TurnSelectionFormState
from tui.screens.session_config.sections.validation.state import ValidationFormState


class ConfigSection(StrEnum):
    PROMPT = "prompt"
    TURN_SELECTION = "turn_selection"
    CONTEXT = "context"
    VALIDATION = "validation"
    RESOLUTION = "resolution"
    PARTICIPANTS = "participants"


@define(frozen=True)
class ModelOptionState:
    id: str
    label: str


@define(frozen=True)
class SessionConfigFormState:
    prompt: PromptFormState
    participants: ParticipantsFormState
    turn_selection: TurnSelectionFormState
    context: ContextFormState
    validation: ValidationFormState
    resolution: ResolutionFormState
