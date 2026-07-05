from hashlib import sha256
from uuid import UUID

from api.modules.engine.models import EngineContext
from api.modules.session_configs.models.participants import Participant
from api.modules.strategies.turn_selection.round_robin import (
    COMPLETED_TURN_EVENT_TYPES,
    COMPLETED_TURN_PARTICIPANT_ID_FIELDS,
    ELIGIBLE_PARTICIPANT_TYPES,
)


class ShuffledTurnSelectionStrategy:
    def choose_participant(self, ctx: EngineContext) -> Participant | None:
        # TODO: Extract this to shared helper
        completed_participant_ids = {
            getattr(event, COMPLETED_TURN_PARTICIPANT_ID_FIELDS[type(event)])
            for event in ctx.events
            if isinstance(event, COMPLETED_TURN_EVENT_TYPES)
        }
        eligible_participants = [
            participant for participant in ctx.participants if participant.type in ELIGIBLE_PARTICIPANT_TYPES
        ]
        ordered_participants = sorted(
            eligible_participants,
            key=lambda participant: (_ordering_key(ctx.seed, 0, participant.id), str(participant.id)),
        )

        for participant in ordered_participants:
            if participant.id not in completed_participant_ids:
                return participant

        return None


def _ordering_key(seed: int, round_number: int, participant_id: UUID) -> int:
    digest = sha256(f"{seed}:{round_number}:{participant_id}".encode()).digest()
    return int.from_bytes(digest, byteorder="big")
