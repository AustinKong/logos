from api_client.models import AIModelRead
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import ContentSwitcher, DataTable, Rule

from tui.screens.session_config.sections.participants.details import ParticipantDetails
from tui.screens.session_config.sections.participants.messages import (
    NewParticipant,
    ParticipantNameChanged,
    RemoveParticipant,
)
from tui.screens.session_config.sections.participants.models import (
    ParticipantFormState,
    ParticipantsFormState,
    agent_participant_form_state,
)
from tui.screens.session_config.sections.participants.table import ParticipantsTable
from tui.shared.textual import on


class ParticipantsSection(Container):
    DEFAULT_CSS = """
    ParticipantsSection {
        height: 100%;
        width: 100%;
        padding: 0;
        layout: horizontal;
    }

    ParticipantsSection #participants-layout {
        height: 100%;
        width: 100%;
    }

    ParticipantsTable {
        height: 100%;
        width: 30%;
    }

    ParticipantsSection #participant-divider {
        width: 1;
    }

    ParticipantDetails {
        height: 100%;
        width: 100%;
    }

    ParticipantsSection #participant-details-switcher {
        height: 100%;
        width: 1fr;
    }
    """

    selected_participant_key = reactive("")

    def __init__(
        self,
        *,
        initial_state: ParticipantsFormState,
        models: list[AIModelRead],
        read_only: bool = False,
    ) -> None:
        super().__init__()
        if not initial_state.participants:
            raise ValueError("ParticipantsSection requires at least one participant")

        self._initial_state = initial_state
        self.selected_participant_key = initial_state.participants[0].key
        self._models = models
        self._read_only = read_only

    def compose(self) -> ComposeResult:
        yield Horizontal(
            ParticipantsTable(
                initial_state=self._initial_state,
                read_only=self._read_only,
            ),
            Rule(orientation="vertical", line_style="heavy", id="participant-divider"),
            ContentSwitcher(
                *self._participant_details(self._initial_state),
                initial=self._details_id(self.selected_participant_key),
                id="participant-details-switcher",
            ),
            id="participants-layout",
        )

    @on(DataTable.RowHighlighted, "ParticipantsTable")
    async def handle_participant_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        self._select_participant(str(event.row_key.value))

    @on(DataTable.RowSelected, "ParticipantsTable")
    async def handle_participant_row_selected(self, event: DataTable.RowSelected) -> None:
        self._select_participant(str(event.row_key.value))

    @on(ParticipantNameChanged)
    def handle_participant_name_changed(self, event: ParticipantNameChanged) -> None:
        self.query_one(ParticipantsTable).update_participant_name(event.participant_key, event.name)

    @on(NewParticipant)
    async def handle_new_participant(self, event: NewParticipant) -> None:
        if self._read_only:
            return

        current_count = len(self._participant_detail_widgets())
        participant = agent_participant_form_state(current_count)
        switcher = self.query_one("#participant-details-switcher", ContentSwitcher)
        await switcher.mount(self._participant_detail(current_count, participant))

        self.query_one(ParticipantsTable).add_participant(participant.key, participant.name)
        self._select_participant(participant.key)
        self.call_after_refresh(self._focus_participants_table)

    @on(RemoveParticipant)
    async def handle_remove_participant(self, event: RemoveParticipant) -> None:
        if self._read_only:
            return

        details = self._participant_detail_widgets()
        if len(details) <= 1:
            return

        removed_index = self._selected_participant_index(details)
        removed_detail = details[removed_index]
        del details[removed_index]

        self.query_one(ParticipantsTable).remove_participant(self.selected_participant_key)
        await removed_detail.remove()
        self._select_participant(details[min(removed_index, len(details) - 1)].participant_key)
        self.call_after_refresh(self._focus_participants_table)

    def form_state(self) -> ParticipantsFormState:
        return ParticipantsFormState(
            participants=[
                details.form_state() for details in self.query(ParticipantDetails).results(ParticipantDetails)
            ]
        )

    def _focus_participants_table(self) -> None:
        self.query_one(ParticipantsTable).focus_participant(self.selected_participant_key)

    def _select_participant(self, selected_key: str) -> None:
        self.selected_participant_key = selected_key
        self.query_one("#participant-details-switcher", ContentSwitcher).current = self._details_id(selected_key)

    def _participant_details(self, participants_state: ParticipantsFormState) -> list[ParticipantDetails]:
        return [
            self._participant_detail(index, participant)
            for index, participant in enumerate(participants_state.participants)
        ]

    def _participant_detail(self, index: int, participant: ParticipantFormState) -> ParticipantDetails:
        return ParticipantDetails(
            participant_index=index,
            initial_state=participant,
            models=self._models,
            read_only=self._read_only,
            id=self._details_id(participant.key),
        )

    def _participant_detail_widgets(self) -> list[ParticipantDetails]:
        return list(self.query(ParticipantDetails).results(ParticipantDetails))

    def _selected_participant_index(self, participants: list[ParticipantDetails]) -> int:
        return next(
            index
            for index, participant in enumerate(participants)
            if participant.participant_key == self.selected_participant_key
        )

    def _details_id(self, participant_key: str) -> str:
        return f"participant-{participant_key}-details"
