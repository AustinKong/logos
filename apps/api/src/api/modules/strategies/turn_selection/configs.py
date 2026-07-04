from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter


class TurnSelectionMode(StrEnum):
    ROUND_ROBIN = "round_robin"
    SHUFFLED = "shuffled"


class RoundRobinTurnSelectionConfig(BaseModel):
    mode: Literal[TurnSelectionMode.ROUND_ROBIN] = TurnSelectionMode.ROUND_ROBIN


class ShuffledTurnSelectionConfig(BaseModel):
    mode: Literal[TurnSelectionMode.SHUFFLED] = TurnSelectionMode.SHUFFLED


type TurnSelectionConfig = Annotated[
    RoundRobinTurnSelectionConfig | ShuffledTurnSelectionConfig,
    Field(discriminator="mode"),
]

TURN_SELECTION_CONFIG_ADAPTER = TypeAdapter(TurnSelectionConfig)
