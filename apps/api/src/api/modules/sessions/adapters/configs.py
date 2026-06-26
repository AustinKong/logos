from api.modules.session_configs.schemas.configs import (
    ContextConfigCreate,
    ContextConfigRead,
    JudgeResolutionConfigCreate,
    JudgeResolutionConfigRead,
    NoneResolutionConfigCreate,
    NoneResolutionConfigRead,
    ResolutionConfigCreate,
    ResolutionConfigRead,
    TurnSelectionConfigCreate,
    TurnSelectionConfigRead,
    ValidationConfigCreate,
    ValidationConfigRead,
)
from api.modules.strategies.context.configs import ContextConfig
from api.modules.strategies.resolution.configs import (
    JudgeResolutionConfig,
    NoneResolutionConfig,
)
from api.modules.strategies.turn_selection.configs import TurnSelectionConfig
from api.modules.strategies.validation.configs import ValidationConfig


def turn_selection_config_from_create(
    turn_selection_create: TurnSelectionConfigCreate,
) -> TurnSelectionConfig:
    return TurnSelectionConfig(mode=turn_selection_create.mode)


def context_config_from_create(context_create: ContextConfigCreate) -> ContextConfig:
    return ContextConfig(mode=context_create.mode)


def validation_config_from_create(validation_create: ValidationConfigCreate) -> ValidationConfig:
    return ValidationConfig(mode=validation_create.mode)


def resolution_config_from_create(
    resolution_create: ResolutionConfigCreate,
) -> JudgeResolutionConfig | NoneResolutionConfig:
    match resolution_create:
        case JudgeResolutionConfigCreate():
            return JudgeResolutionConfig(
                judge_model=resolution_create.judge_model,
                judge_temperature=resolution_create.judge_temperature,
            )
        case NoneResolutionConfigCreate():
            return NoneResolutionConfig()


def turn_selection_config_read_from_config(
    turn_selection_config: TurnSelectionConfig,
) -> TurnSelectionConfigRead:
    return TurnSelectionConfigRead(mode=turn_selection_config.mode)


def context_config_read_from_config(context_config: ContextConfig) -> ContextConfigRead:
    return ContextConfigRead(mode=context_config.mode)


def validation_config_read_from_config(validation_config: ValidationConfig) -> ValidationConfigRead:
    return ValidationConfigRead(mode=validation_config.mode)


def resolution_config_read_from_config(
    resolution_config: JudgeResolutionConfig | NoneResolutionConfig,
) -> ResolutionConfigRead:
    match resolution_config:
        case JudgeResolutionConfig():
            return JudgeResolutionConfigRead(
                judge_model=resolution_config.judge_model,
                judge_temperature=resolution_config.judge_temperature,
            )
        case NoneResolutionConfig():
            return NoneResolutionConfigRead()
