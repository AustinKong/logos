from collections.abc import Sequence

from api.modules.session_configs.models.participants import Participant
from api.modules.tools.models import ToolDefinition


def resolution_vote_tool_definition(eligible_participants: Sequence[Participant]) -> ToolDefinition:
    participants = "\n".join(f"- {participant.name}: {participant.id}" for participant in eligible_participants)

    return ToolDefinition(
        name="submit_resolution_vote",
        title="Submit resolution vote",
        user_description="Select the participant whose position should win the resolution.",
        ai_description=f"Submit your final resolution vote. Eligible participants:\n{participants}",
        scopes=frozenset(),
        parameters={
            "type": "object",
            "properties": {
                "selected_participant_id": {
                    "type": "string",
                    "format": "uuid",
                    "enum": [str(participant.id) for participant in eligible_participants],
                    "description": "ID of the selected eligible participant.",
                },
            },
            "required": ["selected_participant_id"],
            "additionalProperties": False,
        },
    )
