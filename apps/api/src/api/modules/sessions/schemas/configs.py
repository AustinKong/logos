from typing import Annotated, Literal

from pydantic import BaseModel, Field

from api.modules.strategies.context.configs import ContextMode
from api.modules.strategies.resolution.configs import ResolutionMode
from api.modules.strategies.turn_selection.configs import TurnSelectionMode
from api.modules.strategies.validation.configs import ValidationMode


class TurnSelectionConfigCreate(BaseModel):
    mode: TurnSelectionMode = TurnSelectionMode.ROUND_ROBIN


class ContextConfigCreate(BaseModel):
    mode: ContextMode = ContextMode.FULL


class ValidationConfigCreate(BaseModel):
    mode: ValidationMode = ValidationMode.ALLOW_ALL


class JudgeResolutionConfigCreate(BaseModel):
    mode: Literal[ResolutionMode.JUDGE_LLM] = ResolutionMode.JUDGE_LLM
    judge_model: str = "openai/gpt-4o-mini"
    judge_temperature: float = 0.2


class NoneResolutionConfigCreate(BaseModel):
    mode: Literal[ResolutionMode.NONE] = ResolutionMode.NONE


type ResolutionConfigCreate = Annotated[
    JudgeResolutionConfigCreate | NoneResolutionConfigCreate,
    Field(discriminator="mode"),
]
