from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Text, Uuid
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.modules.session_configs.models.participants import Participant
from api.modules.sessions.models.events import Event, EventType


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


class AskUserStartedEvent(Event):
    __tablename__ = "ask_user_started_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    ask_user_id: Mapped[UUID] = mapped_column(index=True, unique=True)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), index=True)
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[list[str]] = mapped_column(JSON)
    cache_entry_id: Mapped[UUID | None] = mapped_column(Uuid, index=True)

    sender: Mapped[Participant] = relationship(Participant, foreign_keys=[sender_id], lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": EventType.ASK_USER_STARTED,
    }


class AskUserCompletedEvent(Event):
    __tablename__ = "ask_user_completed_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    ask_user_id: Mapped[UUID] = mapped_column(index=True, unique=True)
    answer_kind: Mapped[AskUserAnswerKind] = mapped_column(
        SQLAlchemyEnum(
            AskUserAnswerKind,
            name="ask_user_answer_kind",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    answer: Mapped[str] = mapped_column(Text)

    __mapper_args__ = {
        "polymorphic_identity": EventType.ASK_USER_COMPLETED,
    }
