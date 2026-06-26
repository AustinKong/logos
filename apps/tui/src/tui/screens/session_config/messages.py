from collections.abc import Callable

from api_client.models import SessionCreate
from textual.message import Message

type SessionCreateUpdate = Callable[[SessionCreate], SessionCreate]


class SessionConfigDraftChanged(Message):
    def __init__(self, update: SessionCreateUpdate) -> None:
        super().__init__()
        self.update = update
