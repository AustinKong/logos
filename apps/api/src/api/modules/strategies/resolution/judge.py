from api.modules.ai.errors import AIProviderError
from api.modules.ai.models import AIMessage, AIMessageResponseAction, GenerationOptions, MessageRole
from api.modules.ai.service import AIService
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.session_configs.models.participants import JudgeParticipant
from api.modules.sessions.models.events import ResolutionCompletedEvent
from api.modules.strategies.history.full import FullHistoryStrategy
from api.modules.strategies.resolution.configs import JudgeResolutionConfig

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
        # TODO: Should be resolved once we make services can take dtos as judge resolution config will hld judge
        judge: JudgeParticipant,
    ) -> None:
        self._ai_service = ai_service
        self._config = config
        self._judge = judge
        self._history_strategy = FullHistoryStrategy()

    async def resolve(self, ctx: EngineContext) -> EngineOutputStream:
        transcript = self._history_strategy.build_history(ctx)

        response = await self._ai_service.generate_response(
            messages=[
                AIMessage(role=MessageRole.SYSTEM, content=f"{JUDGE_SYSTEM_PROMPT}\n\n{self._judge.system_prompt}"),
                AIMessage(
                    role=MessageRole.USER,
                    content=_build_judge_user_prompt(
                        session_prompt=ctx.prompt,
                        transcript=transcript or "(none)",
                    ),
                ),
            ],
            options=GenerationOptions(
                model=self._judge.model,
                reasoning_effort=self._judge.reasoning_effort,
                verbosity=self._judge.verbosity,
                temperature=self._judge.temperature,
            ),
        )

        if not isinstance(response.action, AIMessageResponseAction):
            raise AIProviderError("AI provider returned an unsupported response action")

        decision = response.action.content

        yield ResolutionCompletedEvent(
            session_id=ctx.session_id,
            decision=decision,
        )


def _build_judge_user_prompt(*, session_prompt: str, transcript: str) -> str:
    return (
        f"Session prompt:\n{session_prompt}\n\n"
        f"Transcript:\n{transcript}\n\n"
        "Write a verdict. Include the decision first, then the main reason."
    )
