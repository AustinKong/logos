from typing import Annotated, Literal

from pydantic import BaseModel, Field

from api.modules.strategies.context.configs import ContextMode
from api.modules.strategies.resolution.configs import ResolutionMode
from api.modules.strategies.turn_selection.configs import TurnSelectionMode
from api.modules.strategies.validation.configs import ValidationMode


class TurnSelectionConfigBase(BaseModel):
    mode: TurnSelectionMode


class TurnSelectionConfigCreate(TurnSelectionConfigBase):
    pass


class TurnSelectionConfigRead(TurnSelectionConfigBase):
    pass


class ContextConfigBase(BaseModel):
    mode: ContextMode


class ContextConfigCreate(ContextConfigBase):
    pass


class ContextConfigRead(ContextConfigBase):
    pass


class ValidationConfigBase(BaseModel):
    mode: ValidationMode


class ValidationConfigCreate(ValidationConfigBase):
    pass


class ValidationConfigRead(ValidationConfigBase):
    pass


class JudgeResolutionConfigBase(BaseModel):
    mode: Literal[ResolutionMode.JUDGE_LLM] = ResolutionMode.JUDGE_LLM
    judge_model: str = Field(min_length=1)
    judge_temperature: float


class JudgeResolutionConfigCreate(JudgeResolutionConfigBase):
    pass


class JudgeResolutionConfigRead(JudgeResolutionConfigBase):
    pass


class NoneResolutionConfigBase(BaseModel):
    mode: Literal[ResolutionMode.NONE] = ResolutionMode.NONE


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
