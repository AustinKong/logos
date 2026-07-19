from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Text, Uuid
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base
from api.db.mixins import TimestampMixin, UUIDMixin
from api.modules.session_configs.models.participants import Participant
from api.modules.tools.ask_user.models import AskUserAnswerKind


class EventType(StrEnum):
    TURN_STARTED = "turn.started"
    TURN_COMPLETED = "turn.completed"
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
    ASK_USER_STARTED = "ask_user.started"
    ASK_USER_COMPLETED = "ask_user.completed"
    RESOLUTION_VOTE = "resolution.vote"


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


class TurnStartedEvent(Event):
    __tablename__ = "turn_started_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    participant_id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), index=True)

    participant: Mapped[Participant] = relationship(Participant, foreign_keys=[participant_id], lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": EventType.TURN_STARTED,
    }


class TurnCompletedEvent(Event):
    __mapper_args__ = {
        "polymorphic_identity": EventType.TURN_COMPLETED,
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
    completed_event: Mapped[MessageCompletedEvent | None] = relationship(
        back_populates="started_event",
        foreign_keys="MessageCompletedEvent.started_event_id",
        uselist=False,
    )

    __mapper_args__ = {
        "polymorphic_identity": EventType.MESSAGE_STARTED,
    }


class MessageCompletedEvent(Event):
    __tablename__ = "message_completed_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    started_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("message_started_events.id"),
        unique=True,
    )
    content: Mapped[str] = mapped_column(Text)

    started_event: Mapped[MessageStartedEvent] = relationship(
        back_populates="completed_event",
        foreign_keys=[started_event_id],
    )

    __mapper_args__ = {
        "polymorphic_identity": EventType.MESSAGE_COMPLETED,
    }


class ReasoningStartedEvent(Event):
    __tablename__ = "reasoning_started_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    completed_event: Mapped[ReasoningCompletedEvent | None] = relationship(
        back_populates="started_event",
        foreign_keys="ReasoningCompletedEvent.started_event_id",
        uselist=False,
    )

    __mapper_args__ = {
        "polymorphic_identity": EventType.REASONING_STARTED,
    }


class ReasoningCompletedEvent(Event):
    __tablename__ = "reasoning_completed_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    started_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("reasoning_started_events.id"),
        unique=True,
    )
    content: Mapped[str] = mapped_column(Text)

    started_event: Mapped[ReasoningStartedEvent] = relationship(
        back_populates="completed_event",
        foreign_keys=[started_event_id],
    )

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


class ResolutionVoteEvent(Event):
    __tablename__ = "resolution_vote_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    selected_participant_id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), index=True)

    selected_participant: Mapped[Participant] = relationship(
        foreign_keys=[selected_participant_id],
        lazy="joined",
    )

    __mapper_args__ = {
        "polymorphic_identity": EventType.RESOLUTION_VOTE,
    }


class AskUserStartedEvent(Event):
    __tablename__ = "ask_user_started_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[list[str]] = mapped_column(JSON)
    cache_entry_id: Mapped[UUID | None] = mapped_column(Uuid, index=True)

    completed_event: Mapped[AskUserCompletedEvent | None] = relationship(
        back_populates="started_event",
        foreign_keys="AskUserCompletedEvent.started_event_id",
        uselist=False,
    )

    __mapper_args__ = {
        "polymorphic_identity": EventType.ASK_USER_STARTED,
    }


class AskUserCompletedEvent(Event):
    __tablename__ = "ask_user_completed_events"

    id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), primary_key=True)
    started_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("ask_user_started_events.id"),
        unique=True,
    )
    answer_kind: Mapped[AskUserAnswerKind] = mapped_column(
        SQLAlchemyEnum(
            AskUserAnswerKind,
            name="ask_user_answer_kind",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    answer: Mapped[str] = mapped_column(Text)

    started_event: Mapped[AskUserStartedEvent] = relationship(
        back_populates="completed_event",
        foreign_keys=[started_event_id],
    )

    __mapper_args__ = {
        "polymorphic_identity": EventType.ASK_USER_COMPLETED,
    }
