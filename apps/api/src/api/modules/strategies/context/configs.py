from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class ContextMode(StrEnum):
    FULL = "full"


class FullContextConfig(BaseModel):
    mode: Literal[ContextMode.FULL] = ContextMode.FULL


ContextConfig = FullContextConfig
