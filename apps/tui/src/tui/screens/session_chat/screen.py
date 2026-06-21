from uuid import UUID

from api_client.models import (
    MessageStartedEventRead,
    SessionCompletedEventRead,
    SessionRead,
)
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.geometry import Spacing
from textual.widgets import Input, Static

from tui.screens.base import BaseScreen
from tui.screens.session_chat.loaders import SessionChatLoader
from tui.screens.session_chat.widgets.event_log import EventLog


# TODO: Make its own widget in widgets/
class ChatPromptInput(Input):
    DEFAULT_CSS = """
    ChatPromptInput {
        width: 1fr;
        border: none;
        background: transparent;
    }
    """

    def on_mount(self) -> None:
        self.styles.height = "1fr"
        self.styles.padding = Spacing(0, 0, 0, 0)


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
                ChatPromptInput(placeholder="Start a session...", id="prompt-input"),
                id="composer",
            ),
            id="session",
        )

    def on_mount(self) -> None:
        self.run_worker(self.load_session(), group="session-load", exclusive=True)

    async def load_session(self) -> None:
        prompt_input = self.query_one("#prompt-input", ChatPromptInput)
        prompt_input.disabled = True
        prompt_input.placeholder = "Session loaded"

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
                self.run_worker(
                    self.stream_events(after_event_id=latest_event_id),
                    group="session-event-stream",
                    exclusive=True,
                )
        except Exception as exc:
            # TODO: Make errors use self.notify instead of appending to logs
            await log.handle_event(exc)

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
                    return
        except Exception as exc:
            await log.handle_event(exc)

    async def stream_tokens(self, *, stream_id: UUID) -> None:
        log = self.query_one(EventLog)

        if self._session is None:
            return

        try:
            async for token in self._loader.stream_tokens(session_id=self._session.id, stream_id=stream_id):
                log.handle_token(token)
        except Exception as exc:
            await log.handle_event(exc)
