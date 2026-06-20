from uuid import UUID

from api_client.models import (
    MessageStartedEventRead,
    SessionCompletedEventRead,
    SessionRead,
)
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Input, Static

from tui.screens.base import BaseScreen
from tui.screens.session.controllers import SessionController
from tui.screens.session.loaders import SessionLoader
from tui.screens.session.widgets.event_log import EventLog


class SessionScreen(BaseScreen):
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

    #prompt-input {
        width: 1fr;
        height: 1fr;
        border: none;
        background: transparent;
        padding: 0;
    }

    """

    def __init__(self, *, controller: SessionController, loader: SessionLoader) -> None:
        super().__init__()
        self._controller = controller
        self._loader = loader
        self._session: SessionRead | None = None

    def compose_content(self) -> ComposeResult:
        yield Vertical(
            EventLog(),
            Horizontal(
                Static(" → ", id="prompt-prefix"),
                Input(placeholder="Start a session...", id="prompt-input"),
                id="composer",
            ),
            id="session",
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "prompt-input":
            return

        await self.start_session(event.value)

    async def start_session(self, prompt: str) -> None:
        prompt = prompt.strip()
        if not prompt:
            return

        prompt_input = self.query_one("#prompt-input", Input)
        prompt_input.value = ""
        prompt_input.disabled = True

        try:
            self._session = await self._controller.create_and_start_session(prompt=prompt)
        except Exception:
            prompt_input.disabled = False
            return

        self.run_worker(self.stream_events(), group="session-event-stream", exclusive=True)

    # TODO: Maybe we move this into event_log itself? Does anything else need to react to the stream?
    async def stream_events(self) -> None:
        log = self.query_one(EventLog)

        if self._session is None:
            return

        try:
            async for event in self._loader.stream_events(session_id=self._session.id):
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
