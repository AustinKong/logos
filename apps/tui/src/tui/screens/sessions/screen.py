from api_client.models.session_summary_read import SessionSummaryRead
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import DataTable
from tui.navigation import Navigate, Route, SessionChatParams, SessionConfigParams
from tui.screens.sessions.loaders import SessionsLoader
from tui.screens.sessions.widgets.session_info import SessionInfo
from tui.screens.sessions.widgets.session_list import SessionList
from tui.shared.textual import on
from tui.widgets.screens.base_screen import BaseScreen


class SessionsScreen(BaseScreen):
    DEFAULT_CSS = """
    #sessions-page {
        height: 1fr;
        width: 100%;
        layout: horizontal;
    }

    SessionList {
        width: 60%;
        height: 100%;
        border: solid $primary;
        padding: 0;
    }

    SessionInfo {
        width: 40%;
        height: 100%;
        border: solid $primary;
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("ctrl+n", "create_session", "New Session", key_display="Ctrl+N"),
        Binding("ctrl+o", "view_config", "View Config", key_display="Ctrl+O"),
    ]

    sessions = reactive[list[SessionSummaryRead]](list)
    selected_session = reactive[SessionSummaryRead | None](None)

    def __init__(
        self,
        *,
        sessions_loader: SessionsLoader,
    ) -> None:
        super().__init__()
        self._sessions_loader = sessions_loader
        self._sessions_by_id: dict[str, SessionSummaryRead] = {}

    def compose_content(self) -> ComposeResult:
        yield Horizontal(
            SessionList().data_bind(sessions=SessionsScreen.sessions),
            SessionInfo().data_bind(session=SessionsScreen.selected_session),
            id="sessions-page",
        )

    def on_mount(self) -> None:
        self.load_sessions()

    @on(DataTable.RowHighlighted, "SessionList")
    def handle_session_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        session_id = str(event.row_key.value)
        self.selected_session = self._sessions_by_id.get(session_id)

    @on(DataTable.RowSelected, "SessionList")
    def handle_session_row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_session = self._sessions_by_id.get(str(event.row_key.value))

        if session := self.selected_session:
            self.post_message(Navigate(Route.SESSION_CHAT, SessionChatParams(session_id=session.id)))

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        if action == "view_config":
            return self.selected_session is not None

        return True

    def action_create_session(self) -> None:
        self.post_message(
            Navigate(
                Route.SESSION_CONFIG,
                SessionConfigParams(on_close=self.load_sessions),
            )
        )

    def action_view_config(self) -> None:
        if session := self.selected_session:
            self.post_message(
                Navigate(
                    Route.SESSION_CONFIG,
                    SessionConfigParams(session_id=session.id),
                )
            )

    @work(group="sessions", exclusive=True)
    async def load_sessions(self) -> None:
        sessions = await self._sessions_loader.list_sessions()
        self._sessions_by_id = {str(session.id): session for session in sessions}
        self.sessions = sessions

        if sessions:
            self.selected_session = sessions[0]
        else:
            self.selected_session = None
