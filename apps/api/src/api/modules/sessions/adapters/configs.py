from typing import assert_never

from api.modules.session_configs.adapters.participants import (
    debater_participant_data_from_create,
    debater_participant_read_from_participant,
    judge_participant_data_from_create,
    judge_participant_read_from_participant,
)
from api.modules.session_configs.models.configs import DebateConfig
from api.modules.session_configs.models.participants import (
    DebaterParticipant,
    JudgeParticipant,
    ParticipantData,
)
from api.modules.session_configs.schemas.configs import (
    FullHistoryConfigCreate,
    FullHistoryConfigRead,
    HistoryConfigCreate,
    HistoryConfigRead,
    JudgeResolutionConfigCreate,
    JudgeResolutionConfigRead,
    NoneResolutionConfigCreate,
    NoneResolutionConfigRead,
    ResolutionConfigCreate,
    ResolutionConfigRead,
    RoundRobinTurnSelectionConfigCreate,
    RoundRobinTurnSelectionConfigRead,
    ShuffledTurnSelectionConfigCreate,
    ShuffledTurnSelectionConfigRead,
    SlidingWindowHistoryConfigCreate,
    SlidingWindowHistoryConfigRead,
    TurnSelectionConfigCreate,
    TurnSelectionConfigRead,
)
from api.modules.session_configs.schemas.session_configs import DebateConfigCreate, DebateConfigRead
from api.modules.strategies.history.configs import FullHistoryConfig, HistoryConfig, SlidingWindowHistoryConfig
from api.modules.strategies.resolution.configs import (
    JudgeResolutionConfig,
    NoneResolutionConfig,
)
from api.modules.strategies.turn_selection.configs import (
    RoundRobinTurnSelectionConfig,
    ShuffledTurnSelectionConfig,
    TurnSelectionConfig,
)


def turn_selection_config_from_create(
    turn_selection_create: TurnSelectionConfigCreate,
) -> TurnSelectionConfig:
    match turn_selection_create:
        case RoundRobinTurnSelectionConfigCreate():
            return RoundRobinTurnSelectionConfig(mode=turn_selection_create.mode)
        case ShuffledTurnSelectionConfigCreate():
            return ShuffledTurnSelectionConfig(mode=turn_selection_create.mode)
        case _ as never:
            assert_never(never)


def history_config_from_create(history_create: HistoryConfigCreate) -> HistoryConfig:
    match history_create:
        case FullHistoryConfigCreate():
            return FullHistoryConfig(mode=history_create.mode)
        case SlidingWindowHistoryConfigCreate():
            return SlidingWindowHistoryConfig(
                mode=history_create.mode,
                window_size=history_create.window_size,
            )
        case _ as never:
            assert_never(never)


def debate_config_from_create(debate_create: DebateConfigCreate) -> DebateConfig:
    return DebateConfig(
        round_count=debate_create.round_count,
        turn_selection_config=turn_selection_config_from_create(debate_create.turn_selection),
        history_config=history_config_from_create(debate_create.history),
    )


def resolution_config_from_create(
    resolution_create: ResolutionConfigCreate,
) -> JudgeResolutionConfig | NoneResolutionConfig:
    match resolution_create:
        case JudgeResolutionConfigCreate():
            return JudgeResolutionConfig(
                mode=resolution_create.mode,
            )
        case NoneResolutionConfigCreate():
            return NoneResolutionConfig(mode=resolution_create.mode)
        case _ as never:
            assert_never(never)


def participant_data_from_resolution_create(resolution_create: ResolutionConfigCreate) -> list[ParticipantData]:
    match resolution_create:
        case JudgeResolutionConfigCreate():
            return [judge_participant_data_from_create(resolution_create.judge)]
        case NoneResolutionConfigCreate():
            return []
        case _ as never:
            assert_never(never)


def participant_data_from_debate_create(debate_create: DebateConfigCreate) -> list[ParticipantData]:
    return [debater_participant_data_from_create(debater) for debater in debate_create.debaters]


def turn_selection_config_read_from_config(
    turn_selection_config: TurnSelectionConfig,
) -> TurnSelectionConfigRead:
    match turn_selection_config:
        case RoundRobinTurnSelectionConfig():
            return RoundRobinTurnSelectionConfigRead(mode=turn_selection_config.mode)
        case ShuffledTurnSelectionConfig():
            return ShuffledTurnSelectionConfigRead(mode=turn_selection_config.mode)
        case _ as never:
            assert_never(never)


def history_config_read_from_config(history_config: HistoryConfig) -> HistoryConfigRead:
    match history_config:
        case FullHistoryConfig():
            return FullHistoryConfigRead(mode=history_config.mode)
        case SlidingWindowHistoryConfig():
            return SlidingWindowHistoryConfigRead(
                mode=history_config.mode,
                window_size=history_config.window_size,
            )
        case _ as never:
            assert_never(never)


def debate_config_read_from_config(
    debate_config: DebateConfig,
    debaters: list[DebaterParticipant],
) -> DebateConfigRead:
    return DebateConfigRead(
        round_count=debate_config.round_count,
        debaters=[debater_participant_read_from_participant(debater) for debater in debaters],
        turn_selection=turn_selection_config_read_from_config(debate_config.turn_selection_config),
        history=history_config_read_from_config(debate_config.history_config),
    )


def resolution_config_read_from_config(
    resolution_config: JudgeResolutionConfig | NoneResolutionConfig,
    judge: JudgeParticipant | None,
) -> ResolutionConfigRead:
    match resolution_config:
        case JudgeResolutionConfig():
            if judge is None:
                raise ValueError("Expected judge participant for judge resolution config")
            return JudgeResolutionConfigRead(
                mode=resolution_config.mode,
                judge=judge_participant_read_from_participant(judge),
            )
        case NoneResolutionConfig():
            return NoneResolutionConfigRead(mode=resolution_config.mode)
        case _ as never:
            assert_never(never)
