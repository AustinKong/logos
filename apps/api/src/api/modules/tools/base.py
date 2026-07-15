from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from api.modules.ai.models import AIToolCall, AIToolDefinition
from api.modules.session_configs.models.participants import Participant
from api.modules.sessions.models.events import Event


@dataclass(frozen=True, slots=True)
class ToolExecutionContext:
    session_id: UUID
    sender: Participant


class Tool(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def title(self) -> str: ...

    @property
    def definition(self) -> AIToolDefinition: ...

    async def execute(self, *, tool_call: AIToolCall, ctx: ToolExecutionContext) -> list[Event]: ...
