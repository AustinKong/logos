from api.modules.session_configs.adapters.participants import participant_read_from_participant
from api.modules.session_configs.models.session_configs import SessionConfig
from api.modules.session_configs.schemas.session_configs import SessionConfigRead
from api.modules.sessions.adapters.configs import (
    history_config_read_from_config,
    resolution_config_read_from_config,
    turn_selection_config_read_from_config,
)


def session_config_read_from_config(config: SessionConfig) -> SessionConfigRead:
    return SessionConfigRead(
        id=config.id,
        prompt=config.prompt,
        seed=config.seed,
        debate_round_count=config.debate_round_count,
        created_at=config.created_at,
        updated_at=config.updated_at,
        participants=[participant_read_from_participant(participant) for participant in config.participants],
        turn_selection=turn_selection_config_read_from_config(config.turn_selection_config),
        history=history_config_read_from_config(config.history_config),
        resolution=resolution_config_read_from_config(config.resolution_config),
    )
