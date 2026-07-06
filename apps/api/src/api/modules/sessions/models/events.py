from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base
from api.db.mixins import TimestampMixin, UUIDMixin
from api.modules.session_configs.models.participants import Participant


class EventType(StrEnum):
    SESSION_STARTED = "session.started"
    SESSION_COMPLETED = "session.completed"
    MESSAGE_STARTED = "message.started"
    MESSAGE_COMPLETED = "message.completed"
    REASONING_STARTED = "reasoning.started"
    REASONING_COMPLETED = "reasoning.completed"
    PROPOSAL_STARTED = "proposal.started"
    PROPOSAL_COMPLETED = "proposal.completed"
    DEBATE_ROUND_STARTED = "debate_round.started"
    DEBATE_ROUND_COMPLETED = "debate_round.completed"
    RESOLUTION_STARTED = "resolution.started"
    RESOLUTION_COMPLETED = "resolution.completed"


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


class ProposalStartedEvent(Event):
    __mapper_args__ = {
        "polymorphic_identity": EventType.PROPOSAL_STARTED,
    }


class ProposalCompletedEvent(Event):
    __mapper_args__ = {
        "polymorphic_identity": EventType.PROPOSAL_COMPLETED,
    }


class ResolutionStartedEvent(Event):
    __mapper_args__ = {
        "polymorphic_identity": EventType.RESOLUTION_STARTED,
    }


class DebateRoundCompletedEvent(Event):
    __mapper_args__ = {
        "polymorphic_identity": EventType.DEBATE_ROUND_COMPLETED,
    }


class MessageStartedEvent(Event):
    __tablename__ = "message_started_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    message_id: Mapped[UUID] = mapped_column(index=True, unique=True)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), index=True)

    sender: Mapped[Participant] = relationship(Participant, foreign_keys=[sender_id], lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": EventType.MESSAGE_STARTED,
    }


class MessageCompletedEvent(Event):
    __tablename__ = "message_completed_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    message_id: Mapped[UUID] = mapped_column(index=True, unique=True)
    content: Mapped[str] = mapped_column(Text)

    __mapper_args__ = {
        "polymorphic_identity": EventType.MESSAGE_COMPLETED,
    }


class ReasoningStartedEvent(Event):
    __tablename__ = "reasoning_started_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    reasoning_id: Mapped[UUID] = mapped_column(index=True, unique=True)
    sender_id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), index=True)

    sender: Mapped[Participant] = relationship(Participant, foreign_keys=[sender_id], lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": EventType.REASONING_STARTED,
    }


class ReasoningCompletedEvent(Event):
    __tablename__ = "reasoning_completed_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    reasoning_id: Mapped[UUID] = mapped_column(index=True, unique=True)
    content: Mapped[str] = mapped_column(Text)

    __mapper_args__ = {
        "polymorphic_identity": EventType.REASONING_COMPLETED,
    }


class DebateRoundStartedEvent(Event):
    __tablename__ = "debate_round_started_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    round_number: Mapped[int] = mapped_column(index=True)

    __mapper_args__ = {
        "polymorphic_identity": EventType.DEBATE_ROUND_STARTED,
    }


class ResolutionCompletedEvent(Event):
    __tablename__ = "resolution_completed_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    decision: Mapped[str] = mapped_column(Text)

    __mapper_args__ = {
        "polymorphic_identity": EventType.RESOLUTION_COMPLETED,
    }
