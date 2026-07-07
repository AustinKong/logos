from api.modules.session_configs.models.session_configs import SessionConfig
from api.modules.session_configs.schemas.session_configs import SessionConfigRead
from api.modules.sessions.adapters.configs import (
    debate_config_read_from_config,
    resolution_config_read_from_config,
)
from api.modules.strategies.resolution.configs import JudgeResolutionConfig


def session_config_read_from_config(config: SessionConfig) -> SessionConfigRead:
    resolution_config = config.resolution_config
    return SessionConfigRead(
        id=config.id,
        prompt=config.prompt,
        seed=config.seed,
        created_at=config.created_at,
        updated_at=config.updated_at,
        debate=debate_config_read_from_config(config.debate_config, config.debater_participants),
        resolution=resolution_config_read_from_config(
            resolution_config,
            config.judge_participant if isinstance(resolution_config, JudgeResolutionConfig) else None,
        ),
    )
