from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class AskUserAnswerKind(StrEnum):
    OPTION = "option"
    FREE_TEXT = "free_text"


@dataclass(frozen=True, slots=True)
class AskUserCacheEntryData:
    session_id: UUID
    vector: list[float]
    source_completed_event_id: UUID


@dataclass(frozen=True, slots=True)
class AskUserCacheEntry:
    id: UUID
    session_id: UUID
    source_completed_event_id: UUID
