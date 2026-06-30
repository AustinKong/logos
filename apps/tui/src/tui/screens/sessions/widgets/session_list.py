from api_client.models.session_summary_read import SessionSummaryRead
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import DataTable
from tui.shared.text import truncate
from tui.shared.time import format_datetime

COLUMNS = [
    "ID",
    "Prompt",
    "Modified",
    "Status",
]


class SessionList(DataTable[str]):
    DEFAULT_CSS = """
    SessionList {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("enter", "select_cursor", "Open Session", key_display="Enter", show=True),
    ]

    sessions = reactive[list[SessionSummaryRead]](list)

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns(*COLUMNS)

    def watch_sessions(self, sessions: list[SessionSummaryRead]) -> None:
        self.clear()

        for session in sessions:
            self.add_row(
                str(session.id)[:10],
                truncate(session.prompt, 32),
                format_datetime(session.updated_at),
                session.status.value.title(),
                key=str(session.id),
            )
