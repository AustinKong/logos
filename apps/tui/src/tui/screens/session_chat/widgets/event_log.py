from uuid import UUID

from api_client.api.sessions.stream_session_tokens import TokenRead
from api_client.models.event_read import EventRead
from api_client.models.message_completed_event_read import MessageCompletedEventRead
from api_client.models.message_started_event_read import MessageStartedEventRead
from api_client.models.reasoning_completed_event_read import ReasoningCompletedEventRead
from api_client.models.reasoning_started_event_read import ReasoningStartedEventRead
from textual.containers import VerticalScroll

from tui.screens.session_chat.streamables.base import StreamableWidget
from tui.screens.session_chat.streamables.message import Message
from tui.screens.session_chat.streamables.reasoning import Reasoning


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
            case MessageStartedEventRead():
                message = Message(event=event)
                self._streamable_widgets[event.message_id] = message
                await self.mount(message)
            case MessageCompletedEventRead():
                widget = self._streamable_widgets.get(event.message_id)
                if widget:
                    widget.set_content(event.content)
            case ReasoningStartedEventRead():
                reasoning = Reasoning(event=event)
                self._streamable_widgets[event.reasoning_id] = reasoning
                await self.mount(reasoning)
            case ReasoningCompletedEventRead():
                widget = self._streamable_widgets.get(event.reasoning_id)
                if widget:
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
