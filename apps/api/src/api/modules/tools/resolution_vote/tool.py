from collections.abc import Sequence
from uuid import UUID

from pydantic import BaseModel, ValidationError

from api.modules.ai.models import AIToolCall
from api.modules.session_configs.models.participants import JudgeParticipant, JurorParticipant, Participant
from api.modules.sessions.models.events import Event, ResolutionVoteEvent
from api.modules.tools.base import ToolExecutionContext
from api.modules.tools.errors import InvalidToolArgumentsError, ToolUnavailableError
from api.modules.tools.models import ToolDefinition
from api.modules.tools.resolution_vote.definition import resolution_vote_tool_definition


class ResolutionVoteToolInput(BaseModel):
    selected_participant_id: UUID


class ResolutionVoteTool:
    def __init__(self, *, eligible_participants: Sequence[Participant]) -> None:
        self._definition = resolution_vote_tool_definition(eligible_participants)
        self._eligible_participant_ids = frozenset(participant.id for participant in eligible_participants)
        self._voted = False

    @property
    def definition(self) -> ToolDefinition:
        return self._definition

    async def execute(self, *, tool_call: AIToolCall, ctx: ToolExecutionContext) -> list[Event]:
        if not isinstance(ctx.sender, JudgeParticipant | JurorParticipant):
            raise ToolUnavailableError("Only judges and jurors can submit resolution votes")
        if self._voted:
            raise InvalidToolArgumentsError("Adjudicator already submitted a resolution vote")

        try:
            tool_input = ResolutionVoteToolInput.model_validate(tool_call.arguments)
        except ValidationError as exc:
            raise InvalidToolArgumentsError("AI provider returned an invalid resolution vote") from exc

        if tool_input.selected_participant_id not in self._eligible_participant_ids:
            raise InvalidToolArgumentsError("Resolution vote must select an eligible participant")

        self._voted = True
        return [
            ResolutionVoteEvent(
                session_id=ctx.session_id,
                selected_participant_id=tool_input.selected_participant_id,
            )
        ]
