from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter


class ResolutionMode(StrEnum):
    JUDGE = "judge"
    JURY = "jury"
    NONE = "none"


class JudgeResolutionConfig(BaseModel):
    mode: Literal[ResolutionMode.JUDGE] = ResolutionMode.JUDGE


class JuryResolutionConfig(BaseModel):
    mode: Literal[ResolutionMode.JURY] = ResolutionMode.JURY


class NoneResolutionConfig(BaseModel):
    mode: Literal[ResolutionMode.NONE] = ResolutionMode.NONE


type ResolutionConfig = Annotated[
    JudgeResolutionConfig | JuryResolutionConfig | NoneResolutionConfig,
    Field(discriminator="mode"),
]

RESOLUTION_CONFIG_ADAPTER = TypeAdapter(ResolutionConfig)
