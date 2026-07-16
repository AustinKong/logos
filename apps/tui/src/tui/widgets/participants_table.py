from collections.abc import Callable

from api_client.models import AILanguageModelRead
from textual.binding import Binding
from textual.widgets import DataTable

from tui.navigation import Navigate, ParticipantEditorParams, Route
from tui.screens.participant_editor.models import (
    ParticipantFormState,
    ParticipantsFormState,
    participant_form_state,
)
from tui.shared.textual import on


class ParticipantsTable(DataTable[str]):
    BINDINGS = [
        Binding("enter", "select_cursor", "Edit participant", show=True),
        Binding("ctrl+n", "new_participant", "New Participant", key_display="Ctrl+N", show=True),
        Binding("ctrl+delete", "remove_participant", "Remove Participant", key_display="Ctrl+Del", show=True),
    ]

    def __init__(
        self,
        *,
        initial_state: ParticipantsFormState,
        models: list[AILanguageModelRead],
        allow_multiple: bool,
        read_only: bool = False,
    ) -> None:
        super().__init__()
        self._participants = initial_state
        self._models = models
        self._allow_multiple = allow_multiple
        self._read_only = read_only
        self._selected_participant_key = initial_state.participants[0].key

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_column("Name", key="name")
        self.add_column("Model", key="model")
        for participant in self._participants.participants:
            self.add_row(
                participant.name,
                self._model_label(participant),
                key=participant.key,
            )

    @on(DataTable.RowSelected)
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        participant = next(
            participant
            for participant in self._participants.participants
            if participant.key == str(event.row_key.value)
        )
        self._open_editor(
            participant,
            on_close=lambda updated: self._update_participant(participant.key, updated),
        )

    @on(DataTable.RowHighlighted)
    def handle_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._selected_participant_key = str(event.row_key.value)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "remove_participant" and self.row_count <= 1:
            return False
        if action in {"new_participant", "remove_participant"}:
            return self._allow_multiple and not self._read_only

        return True

    def action_new_participant(self) -> None:
        self._open_editor(
            participant_form_state(len(self._participants.participants)),
            on_close=self._add_participant,
        )

    def action_remove_participant(self) -> None:
        participant_key = self._selected_participant_key
        self._participants = ParticipantsFormState(
            participants=[
                participant for participant in self._participants.participants if participant.key != participant_key
            ]
        )
        self.remove_row(participant_key)

    def form_state(self) -> ParticipantsFormState:
        return self._participants

    def _open_editor(
        self,
        participant: ParticipantFormState,
        *,
        on_close: Callable[[ParticipantFormState], None],
    ) -> None:
        self.post_message(
            Navigate(
                Route.PARTICIPANT_EDITOR,
                ParticipantEditorParams(
                    initial_state=participant,
                    models=self._models,
                    read_only=self._read_only,
                    on_close=on_close,
                ),
            )
        )

    def _add_participant(self, participant: ParticipantFormState) -> None:
        self._participants = ParticipantsFormState(participants=[*self._participants.participants, participant])
        self.add_row(
            participant.name,
            self._model_label(participant),
            key=participant.key,
        )

    def _update_participant(self, participant_key: str, updated_participant: ParticipantFormState) -> None:
        self._participants = ParticipantsFormState(
            participants=[
                updated_participant if participant.key == participant_key else participant
                for participant in self._participants.participants
            ]
        )
        self.update_cell(participant_key, "name", updated_participant.name, update_width=True)
        self.update_cell(participant_key, "model", self._model_label(updated_participant), update_width=True)

    def _model_label(self, participant: ParticipantFormState) -> str:
        if not isinstance(participant.model, str):
            return "No model selected"

        return next(
            (model.label for model in self._models if model.id == participant.model),
            "Unavailable model",
        )
