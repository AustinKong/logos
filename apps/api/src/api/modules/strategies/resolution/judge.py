from api.modules.ai.models import AIMessage, GenerationOptions, MessageRole
from api.modules.ai.service import AIService
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.sessions.models.events import (
    ResolutionCreatedEvent,
    SessionCompletedEvent,
)
from api.modules.strategies.resolution.configs import JudgeResolutionConfig
from api.modules.strategies.transcripts import format_message_transcript

JUDGE_SYSTEM_PROMPT = (
    "You are a neutral judge resolving a structured debate. "
    "Decide the strongest answer to the session prompt using only the transcript."
)


class JudgeResolutionStrategy:
    def __init__(
        self,
        *,
        ai_service: AIService,
        config: JudgeResolutionConfig,
    ) -> None:
        self._ai_service = ai_service
        self._config = config

    async def resolve(self, ctx: EngineContext) -> EngineOutputStream:
        transcript = format_message_transcript(ctx)
        if transcript is None:
            return

        resolution = await self._ai_service.generate_text(
            messages=[
                AIMessage(role=MessageRole.SYSTEM, content=JUDGE_SYSTEM_PROMPT),
                AIMessage(
                    role=MessageRole.USER,
                    content=_build_judge_user_prompt(
                        session_prompt=ctx.session.config.prompt,
                        transcript=transcript,
                    ),
                ),
            ],
            options=GenerationOptions(
                model=self._config.judge_model,
                temperature=self._config.judge_temperature,
            ),
        )
        yield ResolutionCreatedEvent(
            session_id=ctx.session.id,
            resolution=resolution,
        )
        yield SessionCompletedEvent(session_id=ctx.session.id)


def _build_judge_user_prompt(*, session_prompt: str, transcript: str) -> str:
    return (
        f"Session prompt:\n{session_prompt}\n\n"
        f"Transcript:\n{transcript}\n\n"
        "Write a concise verdict. Include the decision first, then the main reason."
    )
