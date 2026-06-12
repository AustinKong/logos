from dataclasses import dataclass
from enum import StrEnum


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class AIProviderPrefix(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"


@dataclass(frozen=True, slots=True)
class AIMessage:
    role: MessageRole
    content: str


@dataclass(frozen=True, slots=True)
class GenerationOptions:
    model: str
    temperature: float | None = None
    max_tokens: int | None = None
