from typing import assert_never

from api.modules.session_configs.adapters.participants import (
    participant_data_from_create,
    participant_read_from_participant,
)
from api.modules.session_configs.models.participants import (
    DebaterParticipant,
    JudgeParticipant,
    JurorParticipant,
    ParticipantData,
    ParticipantType,
)
from api.modules.session_configs.models.session_configs import DebateConfig, ProposalConfig
from api.modules.session_configs.schemas.configs import (
    FullHistoryConfigCreate,
    FullHistoryConfigRead,
    HistoryConfigCreate,
    HistoryConfigRead,
    JudgeResolutionConfigCreate,
    JudgeResolutionConfigRead,
    JuryResolutionConfigCreate,
    JuryResolutionConfigRead,
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
from api.modules.session_configs.schemas.session_configs import (
    DebateConfigCreate,
    DebateConfigRead,
    ProposalConfigCreate,
    ProposalConfigRead,
)
from api.modules.strategies.history.configs import FullHistoryConfig, HistoryConfig, SlidingWindowHistoryConfig
from api.modules.strategies.resolution.configs import (
    JudgeResolutionConfig,
    JuryResolutionConfig,
    NoneResolutionConfig,
    ResolutionConfig,
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


def proposal_config_from_create(proposal_create: ProposalConfigCreate) -> ProposalConfig:
    return ProposalConfig(tools=proposal_create.tools)


def debate_config_from_create(debate_create: DebateConfigCreate) -> DebateConfig:
    return DebateConfig(
        round_count=debate_create.round_count,
        turn_selection_config=turn_selection_config_from_create(debate_create.turn_selection),
        history_config=history_config_from_create(debate_create.history),
        tools=debate_create.tools,
    )


def resolution_config_from_create(
    resolution_create: ResolutionConfigCreate,
) -> ResolutionConfig:
    match resolution_create:
        case JudgeResolutionConfigCreate():
            return JudgeResolutionConfig(
                mode=resolution_create.mode,
            )
        case JuryResolutionConfigCreate():
            return JuryResolutionConfig(mode=resolution_create.mode)
        case NoneResolutionConfigCreate():
            return NoneResolutionConfig(mode=resolution_create.mode)
        case _ as never:
            assert_never(never)


def participant_data_from_resolution_create(resolution_create: ResolutionConfigCreate) -> list[ParticipantData]:
    match resolution_create:
        case JudgeResolutionConfigCreate():
            return [participant_data_from_create(resolution_create.judge, participant_type=ParticipantType.JUDGE)]
        case JuryResolutionConfigCreate():
            return [
                participant_data_from_create(juror, participant_type=ParticipantType.JUROR)
                for juror in resolution_create.jurors
            ]
        case NoneResolutionConfigCreate():
            return []
        case _ as never:
            assert_never(never)


def participant_data_from_debate_create(debate_create: DebateConfigCreate) -> list[ParticipantData]:
    return [
        participant_data_from_create(debater, participant_type=ParticipantType.DEBATER)
        for debater in debate_create.debaters
    ]


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


def proposal_config_read_from_config(proposal_config: ProposalConfig) -> ProposalConfigRead:
    return ProposalConfigRead(tools=proposal_config.tools)


def debate_config_read_from_config(
    debate_config: DebateConfig,
    debaters: list[DebaterParticipant],
) -> DebateConfigRead:
    return DebateConfigRead(
        round_count=debate_config.round_count,
        debaters=[participant_read_from_participant(debater) for debater in debaters],
        turn_selection=turn_selection_config_read_from_config(debate_config.turn_selection_config),
        history=history_config_read_from_config(debate_config.history_config),
        tools=debate_config.tools,
    )


def resolution_config_read_from_config(
    resolution_config: ResolutionConfig,
    judge: JudgeParticipant | None,
    jurors: list[JurorParticipant],
) -> ResolutionConfigRead:
    match resolution_config:
        case JudgeResolutionConfig():
            if judge is None:
                raise ValueError("Expected judge participant for judge resolution config")
            return JudgeResolutionConfigRead(
                mode=resolution_config.mode,
                judge=participant_read_from_participant(judge),
            )
        case JuryResolutionConfig():
            return JuryResolutionConfigRead(
                mode=resolution_config.mode,
                jurors=[participant_read_from_participant(juror) for juror in jurors],
            )
        case NoneResolutionConfig():
            return NoneResolutionConfigRead(mode=resolution_config.mode)
        case _ as never:
            assert_never(never)
