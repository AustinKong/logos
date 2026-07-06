from api.modules.engine.models import EngineContext
from api.modules.session_configs.models.participants import Participant, ParticipantType

ELIGIBLE_PARTICIPANT_TYPES = (ParticipantType.AGENT,)


class RoundRobinTurnSelectionStrategy:
    def order_participants(self, ctx: EngineContext, *, round_number: int) -> list[Participant]:
        return [participant for participant in ctx.participants if participant.type in ELIGIBLE_PARTICIPANT_TYPES]
