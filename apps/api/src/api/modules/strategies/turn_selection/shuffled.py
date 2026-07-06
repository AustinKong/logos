from hashlib import sha256
from uuid import UUID

from api.modules.engine.models import EngineContext
from api.modules.session_configs.models.participants import Participant
from api.modules.strategies.turn_selection.round_robin import ELIGIBLE_PARTICIPANT_TYPES


class ShuffledTurnSelectionStrategy:
    def order_participants(self, ctx: EngineContext, *, round_number: int) -> list[Participant]:
        eligible_participants = [
            participant for participant in ctx.participants if participant.type in ELIGIBLE_PARTICIPANT_TYPES
        ]
        return sorted(
            eligible_participants,
            key=lambda participant: (_ordering_key(ctx.seed, round_number, participant.id), str(participant.id)),
        )


def _ordering_key(seed: int, round_number: int, participant_id: UUID) -> int:
    digest = sha256(f"{seed}:{round_number}:{participant_id}".encode()).digest()
    return int.from_bytes(digest, byteorder="big")
