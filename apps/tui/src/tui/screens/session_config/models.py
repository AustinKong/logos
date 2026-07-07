from enum import StrEnum

from attrs import define

from tui.screens.session_config.sections.debate.models import DebateFormState
from tui.screens.session_config.sections.general.models import GeneralFormState
from tui.screens.session_config.sections.resolution.models import ResolutionFormState


class ConfigSection(StrEnum):
    GENERAL = "general"
    DEBATE = "debate"
    TURN_SELECTION = "turn_selection"
    HISTORY = "history"
    RESOLUTION = "resolution"
    PARTICIPANTS = "participants"


@define(frozen=True)
class SessionConfigFormState:
    general: GeneralFormState
    debate: DebateFormState
    resolution: ResolutionFormState
