from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import AsyncGenerator, Callable, Hashable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from types import TracebackType
from typing import TypeVar, cast
from uuid import UUID

from anyio import BrokenResourceError, ClosedResourceError, create_memory_object_stream
from anyio.streams.memory import MemoryObjectSendStream
from api.modules.streaming.errors import StreamAlreadyOpenError, StreamCursorExpiredError, StreamNotFoundError
from api.modules.streaming.models import BufferLength, StreamClass
from api.modules.streaming.service import StreamSubscription
from api.shared.time import utc_now

StreamItem = TypeVar("StreamItem")


@dataclass(frozen=True, slots=True)
class StreamKey:
    stream_class_name: Hashable
    stream_id: UUID


@dataclass(slots=True)
class StreamState[StreamItem]:
    buffer: deque[StreamItem] | None
    subscribers: set[MemoryObjectSendStream[StreamItem]] = field(default_factory=set)
    expires_at: datetime | None = None
    cleanup_task: asyncio.Task[None] | None = None


@dataclass(slots=True)
class InMemoryStreamSubscription[StreamItem]:
    stream: AsyncGenerator[StreamItem]

    def __aiter__(self) -> AsyncGenerator[StreamItem]:
        return self.stream

    async def __aenter__(self) -> InMemoryStreamSubscription[StreamItem]:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.stream.aclose()


class InMemoryStreamingService:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._streams: dict[StreamKey, StreamState[object]] = {}

    async def open(self, stream_class: StreamClass[StreamItem], stream_id: UUID) -> None:
        async with self._lock:
            key = self._stream_key(stream_class, stream_id)
            state = self._streams.get(key)
            if state is not None:
                raise StreamAlreadyOpenError()

            state = StreamState(buffer=self._create_buffer(stream_class))
            self._streams[key] = cast(StreamState[object], state)

            self._refresh_expiration_locked(stream_class, stream_id, state)

    async def publish(self, stream_class: StreamClass[StreamItem], stream_id: UUID, item: StreamItem) -> None:
        async with self._lock:
            state = self._get_stream_locked(stream_class, stream_id)
            self._refresh_expiration_locked(stream_class, stream_id, state)

            if state.buffer is not None:
                state.buffer.append(item)
            subscribers = tuple(state.subscribers)

            for subscriber in subscribers:
                try:
                    await subscriber.send(item)
                except (BrokenResourceError, ClosedResourceError):
                    await subscriber.aclose()
                    state.subscribers.discard(subscriber)

    async def subscribe(
        self,
        stream_class: StreamClass[StreamItem],
        stream_id: UUID,
        *,
        after: Callable[[StreamItem], bool] | None = None,
    ) -> StreamSubscription[StreamItem]:
        async with self._lock:
            state = self._get_stream_locked(stream_class, stream_id)
            send_stream, receive_stream = create_memory_object_stream[StreamItem](
                max_buffer_size=stream_class.config.subscriber_queue_size
            )
            buffered_items = tuple(state.buffer) if state.buffer is not None else ()
            buffered_items = self._filter_buffered_items(buffered_items, after)
            state.subscribers.add(send_stream)

        async def stream() -> AsyncGenerator[StreamItem]:
            try:
                for item in buffered_items:
                    yield item

                async with receive_stream:
                    async for item in receive_stream:
                        yield item
            finally:
                await send_stream.aclose()

                async with self._lock:
                    state = cast(
                        StreamState[StreamItem] | None,
                        self._streams.get(self._stream_key(stream_class, stream_id)),
                    )
                    if state is not None:
                        state.subscribers.discard(send_stream)

        return InMemoryStreamSubscription(stream())

    def _filter_buffered_items(
        self,
        buffered_items: tuple[StreamItem, ...],
        after: Callable[[StreamItem], bool] | None,
    ) -> tuple[StreamItem, ...]:
        if after is None:
            return buffered_items

        for index, item in enumerate(buffered_items):
            if after(item):
                return buffered_items[index + 1 :]

        raise StreamCursorExpiredError()

    async def close(self, stream_class: StreamClass[StreamItem], stream_id: UUID) -> None:
        async with self._lock:
            state = self._get_stream_locked(stream_class, stream_id)

            if state.cleanup_task is not None:
                state.cleanup_task.cancel()
            self._streams.pop(self._stream_key(stream_class, stream_id), None)
            subscribers = tuple(state.subscribers)

        for subscriber in subscribers:
            await subscriber.aclose()

    def _get_stream_locked(
        self,
        stream_class: StreamClass[StreamItem],
        stream_id: UUID,
    ) -> StreamState[StreamItem]:
        state = self._streams.get(self._stream_key(stream_class, stream_id))
        if state is None:
            raise StreamNotFoundError()

        return cast(StreamState[StreamItem], state)

    def _refresh_expiration_locked(
        self,
        stream_class: StreamClass[StreamItem],
        stream_id: UUID,
        state: StreamState[StreamItem],
    ) -> None:
        if stream_class.config.ttl is None:
            return

        state.expires_at = utc_now() + stream_class.config.ttl
        if state.cleanup_task is not None:
            state.cleanup_task.cancel()
        state.cleanup_task = asyncio.create_task(
            self._cleanup_after_ttl(stream_class, stream_id, stream_class.config.ttl)
        )

    async def _cleanup_after_ttl(
        self,
        stream_class: StreamClass[StreamItem],
        stream_id: UUID,
        ttl: timedelta,
    ) -> None:
        try:
            await asyncio.sleep(ttl.total_seconds())
        except asyncio.CancelledError:
            return

        await self.close(stream_class, stream_id)

    def _create_buffer(self, stream_class: StreamClass[StreamItem]) -> deque[StreamItem] | None:
        buffer_length = stream_class.config.buffer_length
        if buffer_length == 0:
            return None
        if buffer_length == BufferLength.UNBOUNDED:
            return deque()
        if not isinstance(buffer_length, int) or buffer_length < 0:
            raise ValueError("buffer_length must be a non-negative integer or BufferLength.UNBOUNDED")

        return deque(maxlen=buffer_length)

    def _stream_key(self, stream_class: StreamClass[object], stream_id: UUID) -> StreamKey:
        return StreamKey(stream_class_name=stream_class.name, stream_id=stream_id)
