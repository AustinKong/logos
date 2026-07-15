from enum import StrEnum

from attrs import define

from tui.screens.session_config.sections.debate.models import DebateFormState
from tui.screens.session_config.sections.general.models import GeneralFormState
from tui.screens.session_config.sections.proposal.models import ProposalFormState
from tui.screens.session_config.sections.resolution.models import ResolutionFormState


class ConfigSection(StrEnum):
    GENERAL = "general"
    PROPOSAL = "proposal"
    DEBATE = "debate"
    PARTICIPANTS = "participants"
    RESOLUTION = "resolution"


@define(frozen=True)
class SessionConfigFormState:
    general: GeneralFormState
    proposal: ProposalFormState
    debate: DebateFormState
    resolution: ResolutionFormState
