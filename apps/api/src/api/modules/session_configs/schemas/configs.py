from typing import Annotated, Literal

from pydantic import BaseModel, Field

from api.modules.session_configs.schemas.participants import ParticipantCreate, ParticipantRead
from api.modules.strategies.history.configs import HistoryMode
from api.modules.strategies.resolution.configs import ResolutionMode
from api.modules.strategies.turn_selection.configs import TurnSelectionMode


class RoundRobinTurnSelectionConfigBase(BaseModel):
    mode: Literal[TurnSelectionMode.ROUND_ROBIN] = Field(
        TurnSelectionMode.ROUND_ROBIN,
        title="Round robin",
        description="Give each participant a turn in sequence.",
    )


class RoundRobinTurnSelectionConfigCreate(RoundRobinTurnSelectionConfigBase):
    pass


class RoundRobinTurnSelectionConfigRead(RoundRobinTurnSelectionConfigBase):
    pass


class ShuffledTurnSelectionConfigBase(BaseModel):
    mode: Literal[TurnSelectionMode.SHUFFLED] = Field(
        TurnSelectionMode.SHUFFLED,
        title="Shuffled",
        description="Give each participant one turn in a deterministic seeded random order.",
    )


class ShuffledTurnSelectionConfigCreate(ShuffledTurnSelectionConfigBase):
    pass


class ShuffledTurnSelectionConfigRead(ShuffledTurnSelectionConfigBase):
    pass


class FullHistoryConfigBase(BaseModel):
    mode: Literal[HistoryMode.FULL] = Field(
        HistoryMode.FULL,
        title="Full history",
        description="Include every completed turn when generating the next response.",
    )


class FullHistoryConfigCreate(FullHistoryConfigBase):
    pass


class FullHistoryConfigRead(FullHistoryConfigBase):
    pass


class SlidingWindowHistoryConfigBase(BaseModel):
    mode: Literal[HistoryMode.SLIDING_WINDOW] = Field(
        HistoryMode.SLIDING_WINDOW,
        title="Sliding window",
        description="Include only the most recent completed turns when generating the next response.",
    )
    window_size: int = Field(
        ge=1,
        title="Window size",
        description="Number of recent completed turns to include.",
    )


class SlidingWindowHistoryConfigCreate(SlidingWindowHistoryConfigBase):
    pass


class SlidingWindowHistoryConfigRead(SlidingWindowHistoryConfigBase):
    pass


class JudgeResolutionConfigBase(BaseModel):
    mode: Literal[ResolutionMode.JUDGE] = Field(
        ResolutionMode.JUDGE,
        title="Judge",
        description="Use an AI judge to select the final resolution.",
    )


class JudgeResolutionConfigCreate(JudgeResolutionConfigBase):
    judge: ParticipantCreate = Field(
        title="Judge",
        description="Agent that resolves the debate after the final round.",
    )


class JudgeResolutionConfigRead(JudgeResolutionConfigBase):
    judge: ParticipantRead


class JuryResolutionConfigBase(BaseModel):
    mode: Literal[ResolutionMode.JURY] = Field(
        ResolutionMode.JURY,
        title="Jury",
        description="Use a panel of AI jurors to vote on the final resolution.",
    )


class JuryResolutionConfigCreate(JuryResolutionConfigBase):
    jurors: list[ParticipantCreate] = Field(
        min_length=1,
        title="Jurors",
        description="Agents that independently review the debate and vote on its resolution.",
    )


class JuryResolutionConfigRead(JuryResolutionConfigBase):
    jurors: list[ParticipantRead]


class NoneResolutionConfigBase(BaseModel):
    mode: Literal[ResolutionMode.NONE] = Field(
        ResolutionMode.NONE,
        title="No automatic resolution",
        description="Do not select a final resolution automatically.",
    )


class NoneResolutionConfigCreate(NoneResolutionConfigBase):
    pass


class NoneResolutionConfigRead(NoneResolutionConfigBase):
    pass


type ResolutionConfigCreate = Annotated[
    JudgeResolutionConfigCreate | JuryResolutionConfigCreate | NoneResolutionConfigCreate,
    Field(discriminator="mode"),
]

type ResolutionConfigRead = Annotated[
    JudgeResolutionConfigRead | JuryResolutionConfigRead | NoneResolutionConfigRead,
    Field(discriminator="mode"),
]

type HistoryConfigCreate = Annotated[
    FullHistoryConfigCreate | SlidingWindowHistoryConfigCreate,
    Field(discriminator="mode"),
]

type HistoryConfigRead = Annotated[
    FullHistoryConfigRead | SlidingWindowHistoryConfigRead,
    Field(discriminator="mode"),
]

type TurnSelectionConfigCreate = Annotated[
    RoundRobinTurnSelectionConfigCreate | ShuffledTurnSelectionConfigCreate,
    Field(discriminator="mode"),
]

type TurnSelectionConfigRead = Annotated[
    RoundRobinTurnSelectionConfigRead | ShuffledTurnSelectionConfigRead,
    Field(discriminator="mode"),
]
