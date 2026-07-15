from __future__ import annotations

from pydantic import BaseModel, Field

from api.modules.strategies.history.configs import HistoryConfig
from api.modules.strategies.turn_selection.configs import TurnSelectionConfig


class ProposalConfig(BaseModel):
    tools: list[str]


class DebateConfig(BaseModel):
    round_count: int = Field(ge=1)
    turn_selection_config: TurnSelectionConfig
    history_config: HistoryConfig
    tools: list[str]
