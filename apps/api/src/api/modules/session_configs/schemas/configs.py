from typing import Annotated, Literal

from pydantic import BaseModel, Field

from api.modules.strategies.context.configs import ContextMode
from api.modules.strategies.resolution.configs import ResolutionMode
from api.modules.strategies.turn_selection.configs import TurnSelectionMode
from api.modules.strategies.validation.configs import ValidationMode


class TurnSelectionConfigBase(BaseModel):
    mode: TurnSelectionMode = Field(
        title="Round robin",
        description="Give each participant a turn in sequence.",
    )


class TurnSelectionConfigCreate(TurnSelectionConfigBase):
    pass


class TurnSelectionConfigRead(TurnSelectionConfigBase):
    pass


class ContextConfigBase(BaseModel):
    mode: ContextMode = Field(
        title="Full transcript",
        description="Include the full session transcript when generating the next response.",
    )


class ContextConfigCreate(ContextConfigBase):
    pass


class ContextConfigRead(ContextConfigBase):
    pass


class ValidationConfigBase(BaseModel):
    mode: ValidationMode = Field(
        title="Allow all",
        description="Allow every participant response without automated validation.",
    )


class ValidationConfigCreate(ValidationConfigBase):
    pass


class ValidationConfigRead(ValidationConfigBase):
    pass


class JudgeResolutionConfigBase(BaseModel):
    mode: Literal[ResolutionMode.JUDGE_LLM] = Field(
        ResolutionMode.JUDGE_LLM,
        title="Judge LLM",
        description="Use an AI judge to select the final resolution.",
    )
    judge_model: str = Field(
        min_length=1,
        title="Judge model",
        description="Model used by the AI judge to choose the final resolution.",
    )
    judge_temperature: float = Field(
        title="Judge temperature",
        description="Sampling temperature used by the AI judge.",
    )


class JudgeResolutionConfigCreate(JudgeResolutionConfigBase):
    pass


class JudgeResolutionConfigRead(JudgeResolutionConfigBase):
    pass


class NoneResolutionConfigBase(BaseModel):
    mode: Literal[ResolutionMode.NONE] = Field(
        ResolutionMode.NONE,
        title="No automatic resolution",
        description="Do not select a final resolution automatically.",
    )


class NoneResolutionConfigCreate(NoneResolutionConfigBase):
    pass


class NoneResolutionConfigRead(NoneResolutionConfigBase):
    pass


type ResolutionConfigCreate = Annotated[
    JudgeResolutionConfigCreate | NoneResolutionConfigCreate,
    Field(discriminator="mode"),
]

type ResolutionConfigRead = Annotated[
    JudgeResolutionConfigRead | NoneResolutionConfigRead,
    Field(discriminator="mode"),
]
