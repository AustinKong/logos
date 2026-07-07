from api.modules.engine.models import EngineContext
from api.modules.session_configs.models.participants import DebaterParticipant


class RoundRobinTurnSelectionStrategy:
    def order_participants(self, ctx: EngineContext, *, round_number: int) -> list[DebaterParticipant]:
        return ctx.debaters
