from enum import StrEnum

from attrs import define

from tui.screens.session_config.sections.general.models import GeneralFormState
from tui.screens.session_config.sections.history.models import HistoryFormState
from tui.screens.session_config.sections.participants.models import ParticipantsFormState
from tui.screens.session_config.sections.resolution.models import ResolutionFormState
from tui.screens.session_config.sections.turn_selection.models import TurnSelectionFormState


class ConfigSection(StrEnum):
    GENERAL = "general"
    TURN_SELECTION = "turn_selection"
    HISTORY = "history"
    RESOLUTION = "resolution"
    PARTICIPANTS = "participants"


@define(frozen=True)
class SessionConfigFormState:
    general: GeneralFormState
    participants: ParticipantsFormState
    turn_selection: TurnSelectionFormState
    history: HistoryFormState
    resolution: ResolutionFormState
