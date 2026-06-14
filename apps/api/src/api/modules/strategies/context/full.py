from api.modules.ai.models import AIMessage, MessageRole
from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import ParticipantMessageEvent
from api.modules.sessions.models.participants import AgentParticipant


class FullContextStrategy:
    def build_messages(self, ctx: EngineContext, agent: AgentParticipant) -> list[AIMessage]:
        transcript = _format_transcript(ctx)
        return [
            AIMessage(role=MessageRole.SYSTEM, content=agent.system_prompt),
            AIMessage(
                role=MessageRole.USER,
                content=(
                    f"Session prompt:\n{ctx.session.prompt}\n\n"
                    f"Transcript so far:\n{transcript}\n\n"
                    f"Respond as {agent.name}."
                ),
            ),
        ]


def _format_transcript(ctx: EngineContext) -> str:
    participant_names = {participant.id: participant.name for participant in ctx.participants}
    lines = [
        f"{participant_names.get(event.sender_id, 'Unknown participant')}: {event.content}"
        for event in ctx.events
        if isinstance(event, ParticipantMessageEvent)
    ]
    return "\n".join(lines) if lines else "(none)"
