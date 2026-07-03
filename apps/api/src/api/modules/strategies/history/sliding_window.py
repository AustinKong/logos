from api.modules.engine.models import EngineContext
from api.modules.strategies.history.configs import SlidingWindowHistoryConfig
from api.modules.strategies.history.transcripts import format_message_transcript


class SlidingWindowHistoryStrategy:
    def __init__(self, *, config: SlidingWindowHistoryConfig) -> None:
        self._config = config

    def build_history(self, ctx: EngineContext) -> str | None:
        return format_message_transcript(ctx, limit=self._config.window_size)
