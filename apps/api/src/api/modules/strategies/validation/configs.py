from enum import StrEnum
from typing import Literal

from pydantic import BaseModel


class ValidationMode(StrEnum):
    ALLOW_ALL = "allow_all"


class AllowAllValidationConfig(BaseModel):
    mode: Literal[ValidationMode.ALLOW_ALL] = ValidationMode.ALLOW_ALL


ValidationConfig = AllowAllValidationConfig
