import secrets
from typing import assert_never
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlAlchemyDb
from sqlalchemy.orm import selectinload

from api.modules.ai.models import ReasoningEffort, Verbosity
from api.modules.ai.service import AIService
from api.modules.session_configs.constants import DEFAULT_SESSION_CONFIG_ID
from api.modules.session_configs.errors import (
    SessionConfigNotFoundError,
    UnsupportedParticipantModelError,
    UnsupportedReasoningModelError,
)
from api.modules.session_configs.models.configs import DebateConfig, ProposalConfig
from api.modules.session_configs.models.participants import (
    DebaterParticipant,
    JudgeParticipant,
    JurorParticipant,
    ParticipantData,
    ParticipantType,
)
from api.modules.session_configs.models.session_configs import SessionConfig
from api.modules.strategies.history.configs import FullHistoryConfig
from api.modules.strategies.resolution.configs import NoneResolutionConfig, ResolutionConfig
from api.modules.strategies.turn_selection.configs import RoundRobinTurnSelectionConfig

DEFAULT_PROMPT = "Evaluate the best architecture for a terminal-first multi-agent debate workflow."
MAX_SEED = 2**63 - 1


class SessionConfigService:
    def __init__(self, *, db: SqlAlchemyDb, ai_service: AIService) -> None:
        self._db = db
        self._ai_service = ai_service

    def get_default_config(self) -> SessionConfig:
        try:
            # TODO: What happens if the default config listed model becomes unavailable?
            config = self.get_config(DEFAULT_SESSION_CONFIG_ID)
        except SessionConfigNotFoundError:
            default_model = self._ai_service.list_available_language_models()[0].id
            config = self.create_config(
                id=DEFAULT_SESSION_CONFIG_ID,
                prompt=DEFAULT_PROMPT,
                seed=None,
                participants=[
                    ParticipantData(
                        name="Analyst",
                        model=default_model,
                        system_prompt="Argue for the strongest practical answer. Call out implementation risks.",
                        reasoning_effort=ReasoningEffort.NONE,
                        verbosity=Verbosity.MEDIUM,
                        temperature=0.7,
                        type=ParticipantType.DEBATER,
                    ),
                    ParticipantData(
                        name="Critic",
                        model=default_model,
                        system_prompt="Challenge weak assumptions and look for missing edge cases.",
                        reasoning_effort=ReasoningEffort.NONE,
                        verbosity=Verbosity.MEDIUM,
                        temperature=0.7,
                        type=ParticipantType.DEBATER,
                    ),
                    ParticipantData(
                        name="Synthesizer",
                        model=default_model,
                        system_prompt="Synthesize tradeoffs into a clear recommendation.",
                        reasoning_effort=ReasoningEffort.NONE,
                        verbosity=Verbosity.MEDIUM,
                        temperature=0.7,
                        type=ParticipantType.DEBATER,
                    ),
                ],
                debate_config=DebateConfig(
                    round_count=1,
                    turn_selection_config=RoundRobinTurnSelectionConfig(),
                    history_config=FullHistoryConfig(),
                    tools=["ask_user"],
                ),
                proposal_config=ProposalConfig(tools=["ask_user"]),
                resolution_config=NoneResolutionConfig(),
            )

        return config

    def get_config(self, config_id: UUID) -> SessionConfig:
        statement = (
            select(SessionConfig)
            .where(SessionConfig.id == config_id)
            .options(selectinload(SessionConfig._participants))
        )
        config = self._db.execute(statement).scalar_one_or_none()

        if config is None:
            raise SessionConfigNotFoundError()

        return config

    def create_config(
        self,
        *,
        prompt: str,
        seed: int | None,
        proposal_config: ProposalConfig,
        debate_config: DebateConfig,
        participants: list[ParticipantData],
        resolution_config: ResolutionConfig,
        id: UUID | None = None,
        commit: bool = True,
    ) -> SessionConfig:
        models_by_id = {model.id: model for model in self._ai_service.list_available_language_models()}
        for participant in participants:
            model = models_by_id.get(participant.model)
            if model is None:
                raise UnsupportedParticipantModelError()
            if participant.reasoning_effort is not ReasoningEffort.NONE and not model.supports_reasoning:
                raise UnsupportedReasoningModelError()

        if seed is None:
            seed = secrets.randbelow(MAX_SEED + 1)

        config = SessionConfig(
            prompt=prompt,
            seed=seed,
            proposal_config=proposal_config,
            debate_config=debate_config,
            resolution_config=resolution_config,
        )
        if id is not None:
            config.id = id

        self._db.add(config)
        self._db.flush()

        for participant in participants:
            participant_class = None

            match participant.type:
                case ParticipantType.DEBATER:
                    participant_class = DebaterParticipant
                case ParticipantType.JUDGE:
                    participant_class = JudgeParticipant
                case ParticipantType.JUROR:
                    participant_class = JurorParticipant
                case _ as never:
                    assert_never(never)

            self._db.add(
                participant_class(
                    config_id=config.id,
                    name=participant.name,
                    model=participant.model,
                    system_prompt=participant.system_prompt,
                    reasoning_effort=participant.reasoning_effort,
                    verbosity=participant.verbosity,
                    temperature=participant.temperature,
                )
            )

        if commit:
            self._db.commit()
            return self.get_config(config.id)

        self._db.flush()
        return config
