from api_client.models.session_summary_read import SessionSummaryRead
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import DataTable
from tui.navigation import Navigate, Route, SessionChatParams, SessionConfigParams
from tui.screens.base import BaseScreen
from tui.screens.sessions.loaders import SessionsLoader
from tui.screens.sessions.widgets.session_info import SessionInfo
from tui.screens.sessions.widgets.session_list import SessionList


class SessionsScreen(BaseScreen):
    sessions = reactive[list[SessionSummaryRead]](list)
    selected_session = reactive[SessionSummaryRead | None](None)

    BINDINGS = [
        ("n", "create_session", "New Session"),
        ("enter", "open_session", "Open Session"),
    ]

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
        self.run_worker(self.load_sessions(), group="sessions", exclusive=True)

    async def load_sessions(self) -> None:
        sessions = await self._sessions_loader.list_sessions()
        self._sessions_by_id = {str(session.id): session for session in sessions}
        self.sessions = sessions

        if sessions:
            self.selected_session = sessions[0]
        else:
            self.selected_session = None

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if not isinstance(event.data_table, SessionList):
            return

        event.stop()
        session_id = str(event.row_key.value)
        self.selected_session = self._sessions_by_id.get(session_id)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if not isinstance(event.data_table, SessionList):
            return

        event.stop()
        self.selected_session = self._sessions_by_id.get(str(event.row_key.value))
        self.action_open_session()

    def action_create_session(self) -> None:
        self.post_message(Navigate(Route.SESSION_CONFIG, SessionConfigParams(mode="create")))

    # TODO: Maybe shouldn't bind to key, see if we can bind Enter against data table instead of globally instead
    def action_open_session(self) -> None:
        session = self.selected_session
        if session is None:
            return

        self.post_message(
            Navigate(
                Route.SESSION_CHAT,
                SessionChatParams(session_id=session.id),
            )
        )
