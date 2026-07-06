from uuid import UUID

from api_client.api.sessions.stream_session_tokens import TokenRead
from api_client.models.debate_round_started_event_read import DebateRoundStartedEventRead
from api_client.models.event_read import EventRead
from api_client.models.message_completed_event_read import MessageCompletedEventRead
from api_client.models.message_started_event_read import MessageStartedEventRead
from api_client.models.proposal_started_event_read import ProposalStartedEventRead
from api_client.models.reasoning_completed_event_read import ReasoningCompletedEventRead
from api_client.models.reasoning_started_event_read import ReasoningStartedEventRead
from api_client.models.resolution_started_event_read import ResolutionStartedEventRead
from textual.containers import VerticalScroll

from tui.screens.session_chat.streamables.base import StreamableWidget
from tui.screens.session_chat.streamables.message import Message
from tui.screens.session_chat.streamables.reasoning import Reasoning
from tui.screens.session_chat.widgets.divider import Divider


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
        self._streamable_widgets: dict[UUID, StreamableWidget] = {}

    async def handle_event(self, event: EventRead) -> None:
        match event:
            case ProposalStartedEventRead():
                await self.mount(Divider("Proposal"))
            case DebateRoundStartedEventRead():
                await self.mount(Divider(f"Debate round {event.round_number}"))
            case ResolutionStartedEventRead():
                await self.mount(Divider("Resolution"))
            case MessageStartedEventRead():
                message = Message(event=event)
                self._streamable_widgets[event.message_id] = message
                await self.mount(message)
            case MessageCompletedEventRead():
                if widget := self._streamable_widgets.get(event.message_id):
                    widget.set_content(event.content)
            case ReasoningStartedEventRead():
                reasoning = Reasoning(event=event)
                self._streamable_widgets[event.reasoning_id] = reasoning
                await self.mount(reasoning)
            case ReasoningCompletedEventRead():
                if widget := self._streamable_widgets.get(event.reasoning_id):
                    widget.set_content(event.content)
            case _:
                pass

        self.scroll_end(animate=True)

    def handle_token(self, token: TokenRead) -> None:
        widget = self._streamable_widgets.get(token.correlation_id)
        if widget is None:
            return

        widget.append_content(token.content)
        self.scroll_end(animate=True)
