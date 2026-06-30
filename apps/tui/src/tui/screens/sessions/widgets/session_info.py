from api_client.models.session_summary_read import SessionSummaryRead
from textual import getters
from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.reactive import reactive
from textual.widgets import Label, Static
from tui.shared.time import format_datetime


class SessionInfo(Vertical):
    session = reactive[SessionSummaryRead | None](None)

    session_id = getters.query_one("#session-info-id", Static)
    session_created = getters.query_one("#session-info-created", Static)
    session_updated = getters.query_one("#session-info-updated", Static)
    session_status = getters.query_one("#session-info-status", Static)
    session_prompt = getters.query_one("#session-info-prompt", Static)
    session_participants = getters.query_one("#session-info-participants", Static)

    DEFAULT_CSS = """
    SessionInfo {
        height: 100%;
        padding: 0 1;
    }

    SessionInfo .session-info-grid {
        grid-size: 2;
        grid-columns: 1fr 2fr;
        height: auto;
        width: 100%;
    }

    SessionInfo .session-info-text {
        height: auto;
        width: 100%;
    }

    SessionInfo .session-info-list {
        height: auto;
        width: 100%;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Overview", classes="section-label first")
        yield Grid(
            Label("ID", classes="label"),
            Static("No session selected", id="session-info-id"),
            Label("Created", classes="label"),
            Static("-", id="session-info-created"),
            Label("Modified", classes="label"),
            Static("-", id="session-info-updated"),
            Label("Status", classes="label"),
            Static("-", id="session-info-status"),
            classes="session-info-grid",
        )
        yield Label("Prompt", classes="section-label")
        yield Static(
            "Select a session to inspect its prompt and participants.",
            id="session-info-prompt",
            classes="session-info-text",
        )
        yield Label("Participants", classes="section-label")
        yield Static("-", id="session-info-participants", classes="session-info-list")

    def watch_session(self, session: SessionSummaryRead | None) -> None:
        self._render_session(session)

    def _render_session(self, session: SessionSummaryRead | None) -> None:
        if session is None:
            self.session_id.update("No session selected")
            self.session_created.update("-")
            self.session_updated.update("-")
            self.session_status.update("-")
            self.session_prompt.update("Select a session to inspect its prompt and participants.")
            self.session_participants.update("-")
            return

        self.session_id.update(str(session.id))
        self.session_created.update(format_datetime(session.created_at))
        self.session_updated.update(format_datetime(session.updated_at))
        self.session_status.update(session.status.value.title())
        self.session_prompt.update(session.prompt)
        self.session_participants.update(str(session.participant_count))
