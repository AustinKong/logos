from api.modules.ai.errors import AIProviderError
from api.modules.ai.models import AIMessage, AIMessageResponseAction, GenerationOptions, MessageRole
from api.modules.ai.service import AIService
from api.modules.engine.models import EngineContext, EngineOutputStream
from api.modules.engine.timeline.messages import InternalEventVisibility, TurnMessageMode, ai_messages_from_turns
from api.modules.engine.timeline.turns import turns_from_events
from api.modules.session_configs.models.participants import JudgeParticipant
from api.modules.sessions.models.events import ResolutionCompletedEvent
from api.modules.strategies.resolution.configs import JudgeResolutionConfig

JUDGE_SYSTEM_PROMPT = (
    "You are a neutral judge resolving a structured debate. "
    "Decide the strongest answer to the session prompt using only the transcript."
)
JUDGE_USER_PROMPT = (
    "Session prompt:\n{session_prompt}\n\nWrite a verdict. Include the decision first, then the main reason."
)


class JudgeResolutionStrategy:
    def __init__(
        self,
        *,
        ai_service: AIService,
        config: JudgeResolutionConfig,
        judge: JudgeParticipant,
    ) -> None:
        self._ai_service = ai_service
        self._config = config
        self._judge = judge

    async def resolve(self, ctx: EngineContext) -> EngineOutputStream:
        completed_turns, _ = turns_from_events(ctx.events)

        response = await self._ai_service.generate_response(
            messages=[
                AIMessage(role=MessageRole.SYSTEM, content=f"{JUDGE_SYSTEM_PROMPT}\n\n{self._judge.system_prompt}"),
                AIMessage(
                    role=MessageRole.USER,
                    content=JUDGE_USER_PROMPT.format(session_prompt=ctx.prompt),
                ),
                *ai_messages_from_turns(
                    completed_turns,
                    mode=TurnMessageMode.HISTORY,
                    include_internal_events_from=InternalEventVisibility.NONE,
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
