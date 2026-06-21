from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class SessionStatus(StrEnum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"

    @classmethod
    def from_flags(cls, *, has_started: bool, has_completed: bool) -> SessionStatus:
        if has_completed:
            return SessionStatus.COMPLETED
        if has_started:
            return SessionStatus.RUNNING

        return SessionStatus.DRAFT


@dataclass(frozen=True, slots=True)
class SessionSummary:
    id: UUID
    prompt: str
    created_at: datetime
    updated_at: datetime
    participant_count: int
    status: SessionStatus
