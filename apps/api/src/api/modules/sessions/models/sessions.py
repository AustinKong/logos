from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base
from api.db.mixins import TimestampMixin, UUIDMixin
from api.modules.session_configs.models.session_configs import SessionConfig
from api.modules.sessions.models.events import Event


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


class Session(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    config_id: Mapped[UUID] = mapped_column(ForeignKey("session_configs.id"), unique=True, index=True)

    config: Mapped[SessionConfig] = relationship(lazy="raise")
    events: Mapped[list[Event]] = relationship(
        cascade="all, delete-orphan",
        order_by=lambda: Event.created_at,
        lazy="raise",
    )
