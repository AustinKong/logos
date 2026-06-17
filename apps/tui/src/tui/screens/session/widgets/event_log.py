from api_client.models.event_read import EventRead
from api_client.models.participant_message_event_read import ParticipantMessageEventRead
from textual.containers import VerticalScroll
from textual.widgets import Static

from tui.screens.session.widgets.message import Message


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

    def __init__(
        self,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

    async def append(self, event: EventRead | Exception) -> None:
        match event:
            case ParticipantMessageEventRead():
                await self.mount(Message(content=event.content, sender=event.sender, timestamp=event.created_at))
            case Exception():
                await self.mount(Static(f"Error: {event}"))
            case _:
                pass

        self.scroll_end(animate=True)
