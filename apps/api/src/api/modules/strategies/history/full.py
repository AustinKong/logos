from api.modules.engine.models import EngineContext
from api.modules.strategies.history.transcripts import format_message_transcript


class FullHistoryStrategy:
    def build_history(self, ctx: EngineContext) -> str | None:
        return format_message_transcript(ctx)
