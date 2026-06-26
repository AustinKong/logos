from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class TurnSelectionMode(StrEnum):
    ROUND_ROBIN = "round_robin"


class RoundRobinTurnSelectionConfig(BaseModel):
    mode: Literal[TurnSelectionMode.ROUND_ROBIN] = TurnSelectionMode.ROUND_ROBIN


TurnSelectionConfig = RoundRobinTurnSelectionConfig
