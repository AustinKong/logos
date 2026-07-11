from datetime import datetime
from typing import cast
from uuid import UUID

from api_client.models.turn_started_event_read import TurnStartedEventRead
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Static

from tui.screens.session_chat.streamables.base import StreamableWidget
from tui.shared.colors import color_from_id
from tui.shared.time import format_time


class Turn(Vertical):
    DEFAULT_CSS = """
    Turn {
        height: auto;
        width: 100%;
        margin-bottom: 1;
    }

    Turn .turn-sender {
        width: 1fr;
        text-style: bold;
    }
    """

    def __init__(self, *, event: TurnStartedEventRead) -> None:
        super().__init__(classes="turn")
        self._event = event
        self._latest_at = event.created_at
        self._time_widget: Static | None = None
        self._streamable_widgets: dict[UUID, StreamableWidget] = {}

    def compose(self) -> ComposeResult:
        sender = Static(self._event.sender.name, classes="turn-sender")
        accent = self.app.theme_variables["accent"]
        sender.styles.color = color_from_id(self._event.sender.id, accent)

        self._time_widget = Static(format_time(self._latest_at), classes="turn-time muted")
        yield Horizontal(sender, self._time_widget, classes="turn-header")

    async def add(self, widget: Widget, *, created_at: datetime, stream_id: UUID | None = None) -> None:
        await self.mount(widget)
        if stream_id is not None:
            self._streamable_widgets[stream_id] = cast(StreamableWidget, widget)
        self.touch(created_at)

    def append_content(self, stream_id: UUID, content: str) -> None:
        if widget := self._streamable_widgets.get(stream_id):
            widget.append_content(content)

    def set_content(self, stream_id: UUID, content: str, *, created_at: datetime) -> None:
        if widget := self._streamable_widgets.get(stream_id):
            widget.set_content(content)
        self.touch(created_at)

    def touch(self, created_at: datetime) -> None:
        if created_at <= self._latest_at:
            return

        self._latest_at = created_at
        if self._time_widget is not None:
            self._time_widget.update(format_time(created_at))
