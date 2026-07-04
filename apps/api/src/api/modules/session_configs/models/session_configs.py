from __future__ import annotations

from typing import Any

from sqlalchemy import JSON, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base
from api.db.mixins import TimestampMixin, UUIDMixin
from api.modules.session_configs.models.participants import Participant
from api.modules.strategies.history.configs import HISTORY_CONFIG_ADAPTER, HistoryConfig
from api.modules.strategies.resolution.configs import RESOLUTION_CONFIG_ADAPTER, ResolutionConfig
from api.modules.strategies.turn_selection.configs import TURN_SELECTION_CONFIG_ADAPTER, TurnSelectionConfig
from api.modules.strategies.validation.configs import ValidationConfig


class SessionConfig(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "session_configs"

    prompt: Mapped[str] = mapped_column(Text)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    _turn_selection_config: Mapped[dict[str, Any]] = mapped_column("turn_selection_config", JSON, nullable=False)
    _history_config: Mapped[dict[str, Any]] = mapped_column("history_config", JSON, nullable=False)
    _validation_config: Mapped[dict[str, Any]] = mapped_column("validation_config", JSON, nullable=False)
    _resolution_config: Mapped[dict[str, Any]] = mapped_column("resolution_config", JSON, nullable=False)

    participants: Mapped[list[Participant]] = relationship(
        cascade="all, delete-orphan",
        order_by=lambda: Participant.created_at,
        lazy="raise",
    )

    @property
    def turn_selection_config(self) -> TurnSelectionConfig:
        return TURN_SELECTION_CONFIG_ADAPTER.validate_python(self._turn_selection_config)

    @turn_selection_config.setter
    def turn_selection_config(self, config: TurnSelectionConfig) -> None:
        self._turn_selection_config = config.model_dump(mode="json")

    @property
    def history_config(self) -> HistoryConfig:
        return HISTORY_CONFIG_ADAPTER.validate_python(self._history_config)

    @history_config.setter
    def history_config(self, config: HistoryConfig) -> None:
        self._history_config = config.model_dump(mode="json")

    @property
    def validation_config(self) -> ValidationConfig:
        return ValidationConfig.model_validate(self._validation_config)

    @validation_config.setter
    def validation_config(self, config: ValidationConfig) -> None:
        self._validation_config = config.model_dump(mode="json")

    @property
    def resolution_config(self) -> ResolutionConfig:
        return RESOLUTION_CONFIG_ADAPTER.validate_python(self._resolution_config)

    @resolution_config.setter
    def resolution_config(self, config: ResolutionConfig) -> None:
        self._resolution_config = config.model_dump(mode="json")
