from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlAlchemyDb
from sqlalchemy.orm import selectinload

from api.modules.ai.models import ReasoningEffort
from api.modules.ai.service import AIService
from api.modules.session_configs.constants import DEFAULT_SESSION_CONFIG_ID
from api.modules.session_configs.errors import SessionConfigNotFoundError
from api.modules.session_configs.models.participants import (
    AgentParticipant,
    AgentParticipantData,
    ParticipantData,
    ParticipantType,
    UserParticipant,
    UserParticipantData,
)
from api.modules.session_configs.models.session_configs import SessionConfig
from api.modules.strategies.history.configs import FullHistoryConfig, HistoryConfig
from api.modules.strategies.resolution.configs import NoneResolutionConfig, ResolutionConfig
from api.modules.strategies.turn_selection.configs import RoundRobinTurnSelectionConfig, TurnSelectionConfig
from api.modules.strategies.validation.configs import AllowAllValidationConfig, ValidationConfig

DEFAULT_PROMPT = "Evaluate the best architecture for a terminal-first multi-agent debate workflow."


class SessionConfigService:
    def __init__(self, *, db: SqlAlchemyDb, ai_service: AIService) -> None:
        self._db = db
        self._ai_service = ai_service

    def get_default_config(self) -> SessionConfig:
        try:
            # TODO: What happens if the default config listed model becomes unavailable?
            config = self.get_config(DEFAULT_SESSION_CONFIG_ID)
        except:
            default_model = self._ai_service.list_available_models()[0].id
            config = self.create_config(
                id=DEFAULT_SESSION_CONFIG_ID,
                prompt=DEFAULT_PROMPT,
                participants=[
                    AgentParticipantData(
                        name="Analyst",
                        model=default_model,
                        system_prompt="Argue for the strongest practical answer. Call out implementation risks.",
                        reasoning_effort=ReasoningEffort.NONE,
                    ),
                    AgentParticipantData(
                        name="Critic",
                        model=default_model,
                        system_prompt="Challenge weak assumptions and look for missing edge cases.",
                        reasoning_effort=ReasoningEffort.NONE,
                    ),
                    AgentParticipantData(
                        name="Synthesizer",
                        model=default_model,
                        system_prompt="Synthesize tradeoffs into a clear recommendation.",
                        reasoning_effort=ReasoningEffort.NONE,
                    ),
                ],
                turn_selection=RoundRobinTurnSelectionConfig(),
                history=FullHistoryConfig(),
                validation=AllowAllValidationConfig(),
                resolution=NoneResolutionConfig(),
            )

        return config

    def get_config(self, config_id: UUID) -> SessionConfig:
        statement = (
            select(SessionConfig).where(SessionConfig.id == config_id).options(selectinload(SessionConfig.participants))
        )
        config = self._db.execute(statement).scalar_one_or_none()

        if config is None:
            raise SessionConfigNotFoundError()

        return config

    def create_config(
        self,
        *,
        prompt: str,
        participants: list[ParticipantData],
        turn_selection: TurnSelectionConfig,
        history: HistoryConfig,
        validation: ValidationConfig,
        resolution: ResolutionConfig,
        id: UUID | None = None,
        commit: bool = True,
    ) -> SessionConfig:
        config = SessionConfig(
            prompt=prompt,
            turn_selection_config=turn_selection,
            history_config=history,
            validation_config=validation,
            resolution_config=resolution,
        )
        if id is not None:
            config.id = id

        self._db.add(config)
        self._db.flush()

        for participant in participants:
            match participant:
                case AgentParticipantData():
                    self._db.add(
                        AgentParticipant(
                            config_id=config.id,
                            type=ParticipantType.AGENT,
                            name=participant.name,
                            model=participant.model,
                            system_prompt=participant.system_prompt,
                            reasoning_effort=participant.reasoning_effort,
                        )
                    )
                case UserParticipantData():
                    self._db.add(
                        UserParticipant(
                            config_id=config.id,
                            type=ParticipantType.USER,
                            name=participant.name,
                        )
                    )

        if commit:
            self._db.commit()
            return self.get_config(config.id)

        self._db.flush()
        return config
