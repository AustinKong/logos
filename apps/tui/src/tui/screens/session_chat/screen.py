from uuid import UUID

from api_client.models import (
    MessageStartedEventRead,
    SessionCompletedEventRead,
    SessionRead,
)
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import Static

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

    #composer {
        height: 3;
        width: 100%;
        border: solid $primary;
        background: transparent;
        padding: 0;
    }

    #prompt-prefix {
        width: 3;
        height: 1fr;
        content-align: center middle;
        background: transparent;
    }

    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back", key_display="Esc"),
    ]

    chat_input_shown = reactive(False)

    def __init__(
        self,
        *,
        loader: SessionChatLoader,
        session_id: UUID,
    ) -> None:
        super().__init__()
        self._loader = loader
        self._session_id = session_id
        self._session: SessionRead | None = None

    def compose_content(self) -> ComposeResult:
        yield Vertical(
            EventLog(),
            Horizontal(
                Static(" → ", id="prompt-prefix"),
                ChatInput(placeholder="Start a session...", id="prompt-input").data_bind(
                    shown=SessionChatScreen.chat_input_shown
                ),
                id="composer",
            ),
            id="session",
        )

    def on_mount(self) -> None:
        self.load_session()

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
                self.chat_input_shown = True
                self.stream_events(after_event_id=latest_event_id)
        except Exception as exc:
            self.notify(str(exc), title="Failed to load session", severity="error")

    @work(group="session-event-stream", exclusive=True)
    async def stream_events(self, *, after_event_id: UUID | None) -> None:
        log = self.query_one(EventLog)

        if self._session is None:
            return

        try:
            async for event in self._loader.stream_events(session_id=self._session.id, after_event_id=after_event_id):
                await log.handle_event(event)

                if isinstance(event, MessageStartedEventRead):
                    self.run_worker(
                        self.stream_tokens(stream_id=event.message_id),
                        group=f"session-token-stream:{event.message_id}",
                        exclusive=True,
                    )

                if isinstance(event, SessionCompletedEventRead):
                    self.chat_input_shown = False
                    return
        except Exception as exc:
            self.notify(str(exc), title="Session event stream failed", severity="error")

    async def stream_tokens(self, *, stream_id: UUID) -> None:
        log = self.query_one(EventLog)

        if self._session is None:
            return

        try:
            async for token in self._loader.stream_tokens(session_id=self._session.id, stream_id=stream_id):
                log.handle_token(token)
        except Exception as exc:
            self.notify(str(exc), title="Token stream failed", severity="error")
