from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter


class ResolutionMode(StrEnum):
    JUDGE_LLM = "judge_llm"
    NONE = "none"


class JudgeResolutionConfig(BaseModel):
    mode: Literal[ResolutionMode.JUDGE_LLM] = ResolutionMode.JUDGE_LLM


class NoneResolutionConfig(BaseModel):
    mode: Literal[ResolutionMode.NONE] = ResolutionMode.NONE


type ResolutionConfig = Annotated[
    JudgeResolutionConfig | NoneResolutionConfig,
    Field(discriminator="mode"),
]

RESOLUTION_CONFIG_ADAPTER = TypeAdapter(ResolutionConfig)
