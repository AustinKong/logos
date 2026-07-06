from typing import assert_never

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


def resolution_config_from_create(
    resolution_create: ResolutionConfigCreate,
) -> JudgeResolutionConfig | NoneResolutionConfig:
    match resolution_create:
        case JudgeResolutionConfigCreate():
            return JudgeResolutionConfig(
                mode=resolution_create.mode,
                judge_model=resolution_create.judge_model,
                judge_temperature=resolution_create.judge_temperature,
            )
        case NoneResolutionConfigCreate():
            return NoneResolutionConfig(mode=resolution_create.mode)
        case _ as never:
            assert_never(never)


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


def resolution_config_read_from_config(
    resolution_config: JudgeResolutionConfig | NoneResolutionConfig,
) -> ResolutionConfigRead:
    match resolution_config:
        case JudgeResolutionConfig():
            return JudgeResolutionConfigRead(
                mode=resolution_config.mode,
                judge_model=resolution_config.judge_model,
                judge_temperature=resolution_config.judge_temperature,
            )
        case NoneResolutionConfig():
            return NoneResolutionConfigRead(mode=resolution_config.mode)
        case _ as never:
            assert_never(never)
