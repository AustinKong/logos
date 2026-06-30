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


class ParticipantType(StrEnum):
    AGENT = "agent"
    USER = "user"


@dataclass(frozen=True, slots=True)
class AgentParticipantData:
    name: str
    model: str
    system_prompt: str
    type: ParticipantType = ParticipantType.AGENT


@dataclass(frozen=True, slots=True)
class UserParticipantData:
    name: str
    type: ParticipantType = ParticipantType.USER


type ParticipantData = AgentParticipantData | UserParticipantData


class Participant(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "participants"

    __table_args__ = (UniqueConstraint("config_id", "id", name="uq_participants_config_id_id"),)

    config_id: Mapped[UUID] = mapped_column(ForeignKey("session_configs.id"), index=True)
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
