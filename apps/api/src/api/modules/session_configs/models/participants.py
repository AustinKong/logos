from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from api.db.base import Base
from api.db.mixins import TimestampMixin, UUIDMixin
from api.db.types import ShortString
from api.modules.ai.models import ReasoningEffort, Verbosity


class ParticipantType(StrEnum):
    DEBATER = "debater"
    JUDGE = "judge"
    JUROR = "juror"


@dataclass(frozen=True, slots=True)
class ParticipantData:
    name: str
    model: str
    system_prompt: str
    reasoning_effort: ReasoningEffort
    verbosity: Verbosity
    temperature: float
    type: ParticipantType


class Participant(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "participants"

    __table_args__ = (UniqueConstraint("config_id", "id", name="uq_participants_config_id_id"),)

    config_id: Mapped[UUID] = mapped_column(ForeignKey("session_configs.id"), index=True)
    type: Mapped[ParticipantType] = mapped_column(
        SQLAlchemyEnum(
            ParticipantType,
            name="participant_type",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
    )
    name: Mapped[str] = mapped_column(ShortString)
    model: Mapped[str] = mapped_column(ShortString)
    system_prompt: Mapped[str] = mapped_column(Text)
    reasoning_effort: Mapped[ReasoningEffort] = mapped_column(
        SQLAlchemyEnum(
            ReasoningEffort,
            name="reasoning_effort",
            values_callable=lambda enum: [item.value for item in enum],
        ),
    )
    verbosity: Mapped[Verbosity] = mapped_column(
        SQLAlchemyEnum(
            Verbosity,
            name="verbosity",
            values_callable=lambda enum: [item.value for item in enum],
        ),
    )
    temperature: Mapped[float] = mapped_column(Float, nullable=False)

    __mapper_args__ = {
        "polymorphic_on": type,
        "with_polymorphic": "*",
    }


class DebaterParticipant(Participant):
    __mapper_args__ = {
        "polymorphic_identity": ParticipantType.DEBATER,
    }


class JudgeParticipant(Participant):
    __mapper_args__ = {
        "polymorphic_identity": ParticipantType.JUDGE,
    }


class JurorParticipant(Participant):
    __mapper_args__ = {
        "polymorphic_identity": ParticipantType.JUROR,
    }
