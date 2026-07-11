from api_client.api.sessions.stream_session_tokens import TokenRead
from api_client.models.ask_user_completed_event_read import AskUserCompletedEventRead
from api_client.models.ask_user_started_event_read import AskUserStartedEventRead
from api_client.models.debate_round_started_event_read import DebateRoundStartedEventRead
from api_client.models.event_read import EventRead
from api_client.models.message_completed_event_read import MessageCompletedEventRead
from api_client.models.message_started_event_read import MessageStartedEventRead
from api_client.models.proposal_started_event_read import ProposalStartedEventRead
from api_client.models.reasoning_completed_event_read import ReasoningCompletedEventRead
from api_client.models.reasoning_started_event_read import ReasoningStartedEventRead
from api_client.models.resolution_started_event_read import ResolutionStartedEventRead
from api_client.models.turn_completed_event_read import TurnCompletedEventRead
from api_client.models.turn_started_event_read import TurnStartedEventRead
from textual.containers import VerticalScroll
from textual.widgets import Static

from tui.screens.session_chat.streamables.message import Message
from tui.screens.session_chat.streamables.reasoning import Reasoning
from tui.screens.session_chat.widgets.divider import Divider
from tui.screens.session_chat.widgets.turn import Turn


class EventLog(VerticalScroll):
    DEFAULT_CSS = """
    EventLog {
        height: 1fr;
        width: 100%;
        border: solid $primary;
        overflow-y: auto;
        padding: 0 1;
    }
    """

    BORDER_TITLE = "Events"

    def __init__(
        self,
    ) -> None:
        super().__init__()
        self._active_turn: Turn | None = None

    async def handle_event(self, event: EventRead) -> None:
        match event:
            case ProposalStartedEventRead():
                await self.mount(Divider("Proposal"))
            case DebateRoundStartedEventRead():
                await self.mount(Divider(f"Debate round {event.round_number}"))
            case ResolutionStartedEventRead():
                await self.mount(Divider("Resolution"))
            case TurnStartedEventRead():
                turn = Turn(event=event)
                self._active_turn = turn
                await self.mount(turn)
            case TurnCompletedEventRead():
                if self._active_turn is not None:
                    self._active_turn.touch(event.created_at)
                self._active_turn = None
            case MessageStartedEventRead():
                if self._active_turn is not None:
                    await self._active_turn.add(
                        Message(),
                        created_at=event.created_at,
                        stream_id=event.message_id,
                    )
            case MessageCompletedEventRead():
                if self._active_turn is not None:
                    self._active_turn.set_content(
                        event.message_id,
                        event.content,
                        created_at=event.created_at,
                    )
            case ReasoningStartedEventRead():
                if self._active_turn is not None:
                    await self._active_turn.add(
                        Reasoning(),
                        created_at=event.created_at,
                        stream_id=event.reasoning_id,
                    )
            case ReasoningCompletedEventRead():
                if self._active_turn is not None:
                    self._active_turn.set_content(
                        event.reasoning_id,
                        event.content,
                        created_at=event.created_at,
                    )
            case AskUserStartedEventRead():
                # TODO: Extract these into their own widgets.
                if self._active_turn is not None:
                    await self._active_turn.add(
                        Static(f"Asked: {event.question}"),
                        created_at=event.created_at,
                    )
            case AskUserCompletedEventRead():
                if self._active_turn is not None:
                    await self._active_turn.add(
                        Static(f"Answer: {event.answer}"),
                        created_at=event.created_at,
                    )
            case _:
                pass

        self.scroll_end(animate=True)

    def handle_token(self, token: TokenRead) -> None:
        if self._active_turn is None:
            return

        # TODO: Only forcefully scroll end if user is already at the bottom of the log. Otherwise, don't scroll down and let them read the log
        self._active_turn.append_content(token.correlation_id, token.content)
        self.scroll_end(animate=True)
