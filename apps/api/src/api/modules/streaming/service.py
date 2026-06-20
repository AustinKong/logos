from collections.abc import AsyncIterator, Callable
from types import TracebackType
from typing import Protocol, Self, TypeVar
from uuid import UUID

from api.modules.streaming.models import StreamClass

StreamItem = TypeVar("StreamItem")
StreamItem_co = TypeVar("StreamItem_co", covariant=True)


class StreamSubscription(Protocol[StreamItem_co]):
    def __aiter__(self) -> AsyncIterator[StreamItem_co]: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...


class StreamingService(Protocol):
    async def open(self, stream_class: StreamClass[StreamItem], stream_id: UUID) -> None: ...

    async def publish(self, stream_class: StreamClass[StreamItem], stream_id: UUID, item: StreamItem) -> None: ...

    async def subscribe(
        self,
        stream_class: StreamClass[StreamItem],
        stream_id: UUID,
        *,
        after: Callable[[StreamItem], bool] | None = None,
    ) -> StreamSubscription[StreamItem]:
        """Subscribe to a stream instance.

        `stream_class` identifies the configured kind of stream, including its buffering and TTL behavior.
        `after`, when provided, is matched against buffered replay items and only items after the match are emitted.
        """
        ...

    async def close(self, stream_class: StreamClass[StreamItem], stream_id: UUID) -> None: ...
