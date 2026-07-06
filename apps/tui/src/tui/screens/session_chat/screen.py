from uuid import UUID

from api_client.models import (
    MessageStartedEventRead,
    ReasoningStartedEventRead,
    SessionCompletedEventRead,
    SessionRead,
)
from httpx import HTTPStatusError
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.reactive import reactive

from tui.screens.session_chat.controllers import SessionChatController
from tui.screens.session_chat.loaders import SessionChatLoader
from tui.screens.session_chat.widgets.chat_input import ChatInput
from tui.screens.session_chat.widgets.event_log import EventLog
from tui.widgets.screens.base_screen import BaseScreen


class SessionChatScreen(BaseScreen):
    DEFAULT_CSS = """
    #session {
        height: 1fr;
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back", key_display="Esc"),
        Binding("ctrl+e", "export_session", "Export Session", key_display="Ctrl+E"),
    ]

    chat_input_shown = reactive(False, recompose=True)

    def __init__(
        self,
        *,
        controller: SessionChatController,
        loader: SessionChatLoader,
        session_id: UUID,
    ) -> None:
        super().__init__()
        self._controller = controller
        self._loader = loader
        self._session_id = session_id
        self._session: SessionRead | None = None

    def compose_content(self) -> ComposeResult:
        with Vertical(id="session"):
            yield EventLog()

            if self.chat_input_shown:
                yield ChatInput(placeholder="Start a session...")

    def on_mount(self) -> None:
        self.load_session()

    def action_export_session(self) -> None:
        self.export_session()

    @work(group="session-load", exclusive=True)
    async def load_session(self) -> None:
        log = self.query_one(EventLog)
        try:
            self._session = await self._loader.get_session(session_id=self._session_id)
            events = await self._loader.get_events(session_id=self._session.id)
            latest_event_id: UUID | None = None
            completed = False

            for event in events:
                latest_event_id = event.id
                await log.handle_event(event)

                if isinstance(event, SessionCompletedEventRead):
                    completed = True

            if not completed:
                self.stream_events(after_event_id=latest_event_id)
        except Exception as exc:
            self.notify(str(exc), title="Failed to load session", severity="error")

    @work(group="session-export", exclusive=True)
    async def export_session(self) -> None:
        try:
            path = await self._controller.export_session(session_id=self._session_id)
            self.notify(f"Exported session to {path}")
        except Exception as exc:
            self.notify(str(exc), title="Failed to export session", severity="error")

    @work(group="session-event-stream", exclusive=True)
    async def stream_events(self, *, after_event_id: UUID | None) -> None:
        log = self.query_one(EventLog)

        if self._session is None:
            return

        try:
            async for event in self._loader.stream_events(session_id=self._session.id, after_event_id=after_event_id):
                await log.handle_event(event)

                match event:
                    case MessageStartedEventRead():
                        self.run_worker(
                            self.stream_tokens(stream_id=event.message_id),
                            group=f"session-token-stream:{event.message_id}",
                            exclusive=True,
                        )
                    case ReasoningStartedEventRead():
                        self.run_worker(
                            self.stream_tokens(stream_id=event.reasoning_id),
                            group=f"session-token-stream:{event.reasoning_id}",
                            exclusive=True,
                        )
                    case SessionCompletedEventRead():
                        self.chat_input_shown = False
                        return
        except HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return

            self.notify(str(exc), title="Session event stream failed", severity="error")
        except Exception as exc:
            self.notify(str(exc), title="Session event stream failed", severity="error")

    async def stream_tokens(self, *, stream_id: UUID) -> None:
        log = self.query_one(EventLog)

        if self._session is None:
            return

        try:
            async for token in self._loader.stream_tokens(session_id=self._session.id, stream_id=stream_id):
                log.handle_token(token)
        except HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return

            self.notify(str(exc), title="Token stream failed", severity="error")
        except Exception as exc:
            self.notify(str(exc), title="Token stream failed", severity="error")
