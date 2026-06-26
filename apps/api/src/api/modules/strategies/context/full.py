from api.modules.ai.models import AIMessage, MessageRole
from api.modules.engine.models import EngineContext
from api.modules.session_configs.models.participants import AgentParticipant
from api.modules.strategies.transcripts import format_message_transcript


class FullContextStrategy:
    def build_messages(self, ctx: EngineContext, agent: AgentParticipant) -> list[AIMessage]:
        transcript = format_message_transcript(ctx, empty_text="(none)")
        return [
            AIMessage(role=MessageRole.SYSTEM, content=agent.system_prompt),
            AIMessage(
                role=MessageRole.USER,
                content=(
                    f"Session prompt:\n{ctx.session.config.prompt}\n\n"
                    f"Transcript so far:\n{transcript}\n\n"
                    f"Respond as {agent.name}."
                ),
            ),
        ]
