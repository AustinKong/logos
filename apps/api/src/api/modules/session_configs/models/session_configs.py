from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import JSON, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base
from api.db.mixins import TimestampMixin, UUIDMixin
from api.modules.session_configs.models.participants import (
    DebaterParticipant,
    JudgeParticipant,
    JurorParticipant,
    Participant,
)
from api.modules.strategies.history.configs import HistoryConfig
from api.modules.strategies.resolution.configs import RESOLUTION_CONFIG_ADAPTER, ResolutionConfig
from api.modules.strategies.turn_selection.configs import TurnSelectionConfig


class ProposalConfig(BaseModel):
    tools: list[str]


class DebateConfig(BaseModel):
    round_count: int = Field(ge=1)
    turn_selection_config: TurnSelectionConfig
    history_config: HistoryConfig
    tools: list[str]


class SessionConfig(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "session_configs"

    prompt: Mapped[str] = mapped_column(Text)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    _proposal_config: Mapped[dict[str, Any]] = mapped_column("proposal_config", JSON, nullable=False)
    _debate_config: Mapped[dict[str, Any]] = mapped_column("debate_config", JSON, nullable=False)
    _resolution_config: Mapped[dict[str, Any]] = mapped_column("resolution_config", JSON, nullable=False)

    # Prefer using typed accessors for participants
    _participants: Mapped[list[Participant]] = relationship(
        cascade="all, delete-orphan",
        order_by=lambda: Participant.created_at,
        lazy="raise",
    )

    @property
    def proposal_config(self) -> ProposalConfig:
        return ProposalConfig.model_validate(self._proposal_config)

    @proposal_config.setter
    def proposal_config(self, config: ProposalConfig) -> None:
        self._proposal_config = config.model_dump(mode="json")

    @property
    def debate_config(self) -> DebateConfig:
        return DebateConfig.model_validate(self._debate_config)

    @debate_config.setter
    def debate_config(self, config: DebateConfig) -> None:
        self._debate_config = config.model_dump(mode="json")

    @property
    def resolution_config(self) -> ResolutionConfig:
        return RESOLUTION_CONFIG_ADAPTER.validate_python(self._resolution_config)

    @resolution_config.setter
    def resolution_config(self, config: ResolutionConfig) -> None:
        self._resolution_config = config.model_dump(mode="json")

    @property
    def debater_participants(self) -> list[DebaterParticipant]:
        return [participant for participant in self._participants if isinstance(participant, DebaterParticipant)]

    @property
    def judge_participant(self) -> JudgeParticipant:
        judges = [participant for participant in self._participants if isinstance(participant, JudgeParticipant)]
        if len(judges) != 1:
            raise ValueError(f"Expected exactly one JudgeParticipant, found {len(judges)}")
        return judges[0]

    @property
    def juror_participants(self) -> list[JurorParticipant]:
        return [participant for participant in self._participants if isinstance(participant, JurorParticipant)]
