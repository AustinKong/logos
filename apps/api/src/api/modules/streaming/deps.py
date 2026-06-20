from datetime import timedelta

from api.modules.engine.models import Token
from api.modules.sessions.models.events import Event
from api.modules.streaming.implementations.in_memory import InMemoryStreamingService
from api.modules.streaming.models import BufferLength, StreamClass, StreamConfig
from api.modules.streaming.service import StreamingService

SESSION_EVENT_STREAM = StreamClass[Event](
    name="session.events",
    config=StreamConfig(buffer_length=100, ttl=timedelta(minutes=30)),
)
TOKEN_STREAM = StreamClass[Token](
    name="tokens",
    config=StreamConfig(buffer_length=BufferLength.UNBOUNDED, ttl=timedelta(minutes=5)),
)

_streaming_service = InMemoryStreamingService()


def get_streaming_service() -> StreamingService:
    return _streaming_service
