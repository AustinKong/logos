from datetime import datetime
from uuid import uuid4

from api_client.models import (
    ParticipantMessageEventRead,
    ParticipantRead,
    ParticipantType,
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

DUMMY_MESSAGES = [
    (
        "Pragmatist",
        "pragmatist",
        "AI agents are worth introducing when they replace a narrow, repeated workflow with clear inputs, observable outputs, and a cheap rollback path.",
        "2026-06-15T22:30:00+00:00",
    ),
    (
        "Skeptic",
        "skeptic",
        "The risk is pretending the prototype is production-ready. Before rollout, define failure modes, logging, human review points, and cost limits.",
        "2026-06-15T22:30:08+00:00",
    ),
    (
        "Pragmatist",
        "pragmatist",
        "For a first release, I would keep the agent boxed into draft generation or triage. The system should show its work, ask for confirmation on irreversible steps, and write every decision to the event log.",
        "2026-06-15T22:30:18+00:00",
    ),
    (
        "Skeptic",
        "skeptic",
        "That still needs a kill switch and a boring fallback. If the model provider is slow, expensive, or returns low-confidence output, the app should degrade into a manual workflow instead of blocking the operator.",
        "2026-06-15T22:30:29+00:00",
    ),
    (
        "Judge",
        "judge",
        "Start with one internal workflow where mistakes are low impact, measure whether the agent saves time, and only expand after the team can explain and operate it.",
        "2026-06-15T22:30:41+00:00",
    ),
]


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
        self._participant_names = {}

    def compose_content(self) -> ComposeResult:
        yield Vertical(
            EventLog(id="event-log"),
            Horizontal(
                Static(" → ", id="prompt-prefix"),
                Input(placeholder="Start a session...", id="prompt-input"),
                id="composer",
            ),
            id="session",
        )

    async def on_mount(self) -> None:
        log = self.query_one(EventLog)

        for sender_name, sender_id, content, created_at in DUMMY_MESSAGES:
            await log.append(
                ParticipantMessageEventRead(
                    id=uuid4(),
                    session_id=uuid4(),
                    sender=ParticipantRead(
                        id=uuid4(),
                        type_=ParticipantType.AGENT,
                        name=sender_name,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    ),
                    content=content,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    type_="participant.message",
                )
            )

    # async def on_input_submitted(self, event: Input.Submitted) -> None:
    #     if event.input.id != "prompt-input":
    #         return

    #     await self.start_session(event.value)

    # async def start_session(self, prompt: str) -> None:
    #     prompt = prompt.strip()
    #     if not prompt:
    #         return

    #     prompt_input = self.query_one("#prompt-input", Input)
    #     prompt_input.value = ""
    #     prompt_input.disabled = True

    #     try:
    #         self._session = await self._controller.create_and_start_session(prompt=prompt)
    #     except Exception as exc:
    #         await self._append_error(exc)
    #         prompt_input.disabled = False
    #         return

    #     self._participant_names = {participant.id: participant.name for participant in self._session.participants}
    #     self.run_worker(self.stream_events(), group="session", exclusive=True)

    async def stream_events(self) -> None:
        log = self.query_one(EventLog)

        if self._session is None:
            return

        try:
            async for event in self._loader.stream_events(session_id=self._session.id):
                await log.append(event)

                if isinstance(event, SessionCompletedEventRead):
                    return
        except Exception as exc:
            await log.append(exc)

    # async def _append_resolution(self, event: ResolutionCreatedEventRead) -> None:
    #     await self._append_chat_message(
    #         sender_name="Judge",
    #         sender_id="judge",
    #         content=event.resolution,
    #         created_at=event.created_at.isoformat(),
    #     )
