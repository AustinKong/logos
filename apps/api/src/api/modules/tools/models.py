from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ToolScope(StrEnum):
    PROPOSAL = "proposal"
    DEBATE = "debate"


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    title: str
    user_description: str
    ai_description: str
    scopes: frozenset[ToolScope]
    parameters: dict[str, Any]
