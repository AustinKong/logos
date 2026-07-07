from attrs import define
from tui.screens.session_config.sections.history.models import HistoryFormState
from tui.screens.session_config.sections.participants.models import ParticipantsFormState
from tui.screens.session_config.sections.turn_selection.models import TurnSelectionFormState


# TODO: Move turn selection, history etc. into debate tab?
@define(frozen=True)
class DebateFormState:
    round_count: str
    participants: ParticipantsFormState
    turn_selection: TurnSelectionFormState
    history: HistoryFormState
