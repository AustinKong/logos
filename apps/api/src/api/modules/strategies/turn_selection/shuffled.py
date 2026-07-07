from hashlib import sha256
from uuid import UUID

from api.modules.engine.models import EngineContext
from api.modules.session_configs.models.participants import DebaterParticipant


class ShuffledTurnSelectionStrategy:
    def order_participants(self, ctx: EngineContext, *, round_number: int) -> list[DebaterParticipant]:
        return sorted(
            ctx.debaters,
            key=lambda participant: (_ordering_key(ctx.seed, round_number, participant.id), str(participant.id)),
        )


def _ordering_key(seed: int, round_number: int, participant_id: UUID) -> int:
    digest = sha256(f"{seed}:{round_number}:{participant_id}".encode()).digest()
    return int.from_bytes(digest, byteorder="big")
