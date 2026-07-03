from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter


class HistoryMode(StrEnum):
    FULL = "full"
    SLIDING_WINDOW = "sliding_window"


class FullHistoryConfig(BaseModel):
    mode: Literal[HistoryMode.FULL] = HistoryMode.FULL


class SlidingWindowHistoryConfig(BaseModel):
    mode: Literal[HistoryMode.SLIDING_WINDOW] = HistoryMode.SLIDING_WINDOW
    window_size: int = Field(ge=1)


type HistoryConfig = Annotated[
    FullHistoryConfig | SlidingWindowHistoryConfig,
    Field(discriminator="mode"),
]

HISTORY_CONFIG_ADAPTER = TypeAdapter(HistoryConfig)
