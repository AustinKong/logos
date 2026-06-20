from collections.abc import Hashable
from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum


class BufferLength(StrEnum):
    UNBOUNDED = "unbounded"


@dataclass(frozen=True, slots=True)
class StreamConfig:
    buffer_length: int | BufferLength = 0
    ttl: timedelta | None = None
    subscriber_queue_size: int = 100


@dataclass(frozen=True, slots=True)
class StreamClass[StreamItem]:
    name: Hashable
    config: StreamConfig
