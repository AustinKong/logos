from textual.binding import Binding
from textual.widgets import DataTable

from tui.screens.session_config.sections.participants.messages import (
    NewParticipant,
    RemoveParticipant,
)
from tui.screens.session_config.sections.participants.state import ParticipantsFormState


class ParticipantsTable(DataTable[str]):
    DEFAULT_CSS = """
    ParticipantsTable {
        padding: 0;
    }
    """

    BINDINGS = [
        Binding("ctrl+n", "new_participant", "New Participant", key_display="Ctrl+N", show=True),
        Binding("ctrl+delete", "remove_participant", "Remove Participant", key_display="Ctrl+Del", show=True),
    ]

    def __init__(
        self,
        *,
        initial_state: ParticipantsFormState,
        read_only: bool = False,
    ) -> None:
        super().__init__(id="participants-table")
        self._initial_state = initial_state
        self._read_only = read_only

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_column("Name", key="name")

        for participant in self._initial_state.participants:
            self.add_participant(participant.key, participant.name)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "remove_participant" and self.row_count <= 1:
            return False
        if action in {"new_participant", "remove_participant"}:
            return not self._read_only

        return True

    def action_new_participant(self) -> None:
        if not self._read_only:
            self.post_message(NewParticipant())

    def action_remove_participant(self) -> None:
        if not self._read_only and self.row_count > 1:
            self.post_message(RemoveParticipant())

    def add_participant(self, participant_key: str, name: str) -> None:
        self.add_row(name, key=participant_key)

    def remove_participant(self, participant_key: str) -> None:
        self.remove_row(participant_key)

    def update_participant_name(self, participant_key: str, name: str) -> None:
        self.update_cell(participant_key, "name", name, update_width=True)

    def focus_participant(self, participant_key: str) -> None:
        self.focus()
        self.move_cursor(row=self.get_row_index(participant_key))
