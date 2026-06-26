from pydantic import BaseModel, Field

from api.modules.sessions.models.participants import AgentParticipantConfig
from api.modules.strategies.context.configs import ContextConfig
from api.modules.strategies.resolution.configs import JudgeResolutionConfig, ResolutionConfig
from api.modules.strategies.turn_selection.configs import TurnSelectionConfig
from api.modules.strategies.validation.configs import ValidationConfig


class SessionConfig(BaseModel):
    prompt: str
    agents: list[AgentParticipantConfig] = Field(default_factory=list)
    turn_selection: TurnSelectionConfig = Field(default_factory=TurnSelectionConfig)
    context: ContextConfig = Field(default_factory=ContextConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    resolution: ResolutionConfig = Field(default_factory=JudgeResolutionConfig)
