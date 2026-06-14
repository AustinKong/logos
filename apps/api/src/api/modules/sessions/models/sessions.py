from __future__ import annotations

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base
from api.db.mixins import TimestampMixin, UUIDMixin
from api.modules.sessions.models.events import Event
from api.modules.sessions.models.participants import Participant


class Session(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sessions"

    prompt: Mapped[str] = mapped_column(Text)

    participants: Mapped[list[Participant]] = relationship(
        cascade="all, delete-orphan",
        order_by=lambda: Participant.created_at,
        lazy="raise",
    )
    events: Mapped[list[Event]] = relationship(
        cascade="all, delete-orphan",
        order_by=lambda: Event.created_at,
        lazy="raise",
    )
