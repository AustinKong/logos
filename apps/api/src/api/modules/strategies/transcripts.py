from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import ParticipantMessageEvent

# TODO: More sophisticated transcript formatting in future, e.g. other event types


def format_participant_message_transcript(ctx: EngineContext, *, empty_text: str | None = None) -> str | None:
    participant_names = {participant.id: participant.name for participant in ctx.participants}
    lines = [
        f"{participant_names.get(event.sender_id, 'Unknown participant')}: {event.content}"
        for event in ctx.events
        if isinstance(event, ParticipantMessageEvent)
    ]
    if not lines:
        return empty_text

    return "\n".join(lines)
