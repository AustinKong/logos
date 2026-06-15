from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from api.db.base import Base
from api.db.mixins import TimestampMixin, UUIDMixin


class EventType(StrEnum):
    SESSION_STARTED = "session.started"
    SESSION_COMPLETED = "session.completed"
    PARTICIPANT_MESSAGE = "participant.message"
    PARTICIPANT_VOTE = "participant.vote"
    PARTICIPANT_REMOVED = "participant.removed"
    RESOLUTION_CREATED = "resolution.created"


# Simple events stay in the base events table to avoid unnecessary new tables.
# More complex events use joined tables because they have distinct fields.
class Event(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "events"

    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("sessions.id"),
        index=True,
    )
    type: Mapped[EventType] = mapped_column(
        SQLAlchemyEnum(
            EventType,
            name="event_type",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )

    __mapper_args__ = {
        "polymorphic_on": type,
        "with_polymorphic": "*",
    }


class SessionStartedEvent(Event):
    __mapper_args__ = {
        "polymorphic_identity": EventType.SESSION_STARTED,
    }


class SessionCompletedEvent(Event):
    __mapper_args__ = {
        "polymorphic_identity": EventType.SESSION_COMPLETED,
    }


class ParticipantMessageEvent(Event):
    __tablename__ = "participant_message_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), index=True)
    content: Mapped[str] = mapped_column(Text)

    __mapper_args__ = {
        "polymorphic_identity": EventType.PARTICIPANT_MESSAGE,
    }


class ParticipantVoteEvent(Event):
    __tablename__ = "participant_vote_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    voter_id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), index=True)
    target_id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), index=True)
    reason: Mapped[str] = mapped_column(Text)

    __mapper_args__ = {
        "polymorphic_identity": EventType.PARTICIPANT_VOTE,
    }


class ParticipantRemovedEvent(Event):
    __tablename__ = "participant_removed_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    removed_id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), index=True)

    __mapper_args__ = {
        "polymorphic_identity": EventType.PARTICIPANT_REMOVED,
    }


class ResolutionCreatedEvent(Event):
    __tablename__ = "resolution_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    resolution: Mapped[str] = mapped_column(Text)

    __mapper_args__ = {
        "polymorphic_identity": EventType.RESOLUTION_CREATED,
    }
