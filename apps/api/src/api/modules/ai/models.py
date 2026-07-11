from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field

# Model, Message, ToolCall, Reasoning, Response, and Provider overlap with domain concepts
# or Python reserved words, so prefix them with "AI".


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class AIProviderName(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"


class ReasoningEffort(StrEnum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Verbosity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True, slots=True)
class AILanguageModel:
    id: str
    label: str
    provider: AIProviderName
    supports_reasoning: bool


@dataclass(frozen=True, slots=True)
class AIEmbeddingModel:
    id: str
    label: str
    provider: AIProviderName


@dataclass(frozen=True, slots=True)
class AIMessage:
    role: MessageRole
    content: str


class AIToolCall(BaseModel):
    name: str = Field(min_length=1)
    arguments: dict[str, Any]


@dataclass(frozen=True, slots=True)
class AIToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]


class AIMessageResponseAction(BaseModel):
    type: Literal["message"] = "message"
    content: str = Field(min_length=1)


class AIToolCallsResponseAction(BaseModel):
    type: Literal["tool_calls"] = "tool_calls"
    tool_calls: list[AIToolCall] = Field(min_length=1)


type AIResponseAction = Annotated[
    AIMessageResponseAction | AIToolCallsResponseAction,
    Field(discriminator="type"),
]


# Reasoning cannot exist without a corresponding action
class AIResponse(BaseModel):
    reasoning: str | None = None
    action: AIResponseAction


class AIMessageDelta(BaseModel):
    type: Literal["message.delta"] = "message.delta"
    content: str


class AIReasoningDelta(BaseModel):
    type: Literal["reasoning.delta"] = "reasoning.delta"
    content: str


class AIToolCallEvent(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    tool_call: AIToolCall


type AIResponseEvent = Annotated[
    AIMessageDelta | AIReasoningDelta | AIToolCallEvent,
    Field(discriminator="type"),
]


@dataclass(frozen=True, slots=True)
class GenerationOptions:
    model: str
    tools: Sequence[AIToolDefinition] = ()
    temperature: float | None = None
    max_tokens: int | None = None
    reasoning_effort: ReasoningEffort = ReasoningEffort.NONE
    verbosity: Verbosity = Verbosity.MEDIUM


@dataclass(frozen=True, slots=True)
class EmbeddingOptions:
    model: str


type AIEmbedding = list[float]
