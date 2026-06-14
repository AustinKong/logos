from typing import Protocol

from api.modules.ai.models import AIMessage
from api.modules.engine.models import EngineContext
from api.modules.sessions.models.participants import AgentParticipant


class ContextStrategy(Protocol):
    def build_messages(self, ctx: EngineContext, agent: AgentParticipant) -> list[AIMessage]: ...
