from attrs import define
from tui.screens.participant_editor.models import ParticipantsFormState
from tui.screens.session_config.sections.debate.history.models import HistoryFormState
from tui.screens.session_config.sections.debate.turn_selection.models import TurnSelectionFormState


# TODO: Move turn selection, history etc. into debate tab?
@define(frozen=True)
class DebateFormState:
    round_count: str
    participants: ParticipantsFormState
    turn_selection: TurnSelectionFormState
    history: HistoryFormState
    tools: list[str]
