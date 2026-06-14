from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from api.db.base import Base
from api.db.mixins import TimestampMixin, UUIDMixin
from api.db.types import ShortString


@dataclass(frozen=True, slots=True)
class AgentParticipantConfig:
    name: str
    model: str
    system_prompt: str


class ParticipantType(StrEnum):
    AGENT = "agent"
    USER = "user"
    SYSTEM = "system"


class Participant(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "participants"

    __table_args__ = (UniqueConstraint("session_id", "id", name="uq_participants_session_id_id"),)

    session_id: Mapped[UUID] = mapped_column(ForeignKey("sessions.id"), index=True)
    type: Mapped[ParticipantType] = mapped_column(
        SQLAlchemyEnum(
            ParticipantType,
            name="participant_type",
            values_callable=lambda enum: [item.value for item in enum],
        )
    )
    name: Mapped[str] = mapped_column(ShortString)

    __mapper_args__ = {
        "polymorphic_on": type,
        "with_polymorphic": "*",
    }


class AgentParticipant(Participant):
    __tablename__ = "agent_participants"

    id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), primary_key=True)
    model: Mapped[str] = mapped_column(ShortString)
    system_prompt: Mapped[str] = mapped_column(Text)

    __mapper_args__ = {
        "polymorphic_identity": ParticipantType.AGENT,
    }


class UserParticipant(Participant):
    __tablename__ = "user_participants"

    id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": ParticipantType.USER,
    }


class SystemParticipant(Participant):
    __tablename__ = "system_participants"

    id: Mapped[UUID] = mapped_column(ForeignKey("participants.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": ParticipantType.SYSTEM,
    }
