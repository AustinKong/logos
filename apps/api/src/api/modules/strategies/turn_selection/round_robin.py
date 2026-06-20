from api.modules.engine.models import EngineContext
from api.modules.sessions.models.events import MessageStartedEvent, ParticipantVoteEvent
from api.modules.sessions.models.participants import Participant, ParticipantType

# TODO: Make these constants configurable via constructor passing in.
# ParticipantVoteEvent is here because voting might use turn selection strategy.
COMPLETED_TURN_EVENT_TYPES = (MessageStartedEvent, ParticipantVoteEvent)
COMPLETED_TURN_PARTICIPANT_ID_FIELDS = {
    MessageStartedEvent: "sender_id",
    ParticipantVoteEvent: "voter_id",
}
ELIGIBLE_PARTICIPANT_TYPES = (ParticipantType.AGENT,)


class RoundRobinTurnSelectionStrategy:
    def choose_participant(self, ctx: EngineContext) -> Participant | None:
        completed_participant_ids = {
            getattr(event, COMPLETED_TURN_PARTICIPANT_ID_FIELDS[type(event)])
            for event in ctx.events
            if isinstance(event, COMPLETED_TURN_EVENT_TYPES)
        }

        # TODO: Consider round-related events once rounds are represented in the event log.
        for participant in ctx.participants:
            if participant.type in ELIGIBLE_PARTICIPANT_TYPES and participant.id not in completed_participant_ids:
                return participant

        return None
