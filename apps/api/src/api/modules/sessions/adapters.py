from typing import Any

from api.modules.engine.models import Token
from api.modules.sessions.models.events import (
    Event,
    EventType,
    MessageCompletedEvent,
    MessageStartedEvent,
    ParticipantRemovedEvent,
    ParticipantVoteEvent,
    ResolutionCreatedEvent,
    SessionCompletedEvent,
    SessionStartedEvent,
)
from api.modules.sessions.models.participants import AgentParticipantConfig, Participant
from api.modules.sessions.models.session_configs import SessionConfig
from api.modules.sessions.models.sessions import Session, SessionSummary
from api.modules.sessions.schemas.configs import (
    ContextConfigCreate,
    JudgeResolutionConfigCreate,
    NoneResolutionConfigCreate,
    ResolutionConfigCreate,
    TurnSelectionConfigCreate,
    ValidationConfigCreate,
)
from api.modules.sessions.schemas.events import (
    EventRead,
    MessageCompletedEventRead,
    MessageStartedEventRead,
    ParticipantRemovedEventRead,
    ParticipantVoteEventRead,
    ResolutionCreatedEventRead,
    SessionCompletedEventRead,
    SessionStartedEventRead,
    TokenRead,
)
from api.modules.sessions.schemas.participants import AgentParticipantCreate, ParticipantRead
from api.modules.sessions.schemas.sessions import (
    SessionCreate,
    SessionRead,
    SessionSummaryRead,
)
from api.modules.strategies.context.configs import ContextConfig
from api.modules.strategies.resolution.configs import (
    JudgeResolutionConfig,
    NoneResolutionConfig,
)
from api.modules.strategies.turn_selection.configs import TurnSelectionConfig
from api.modules.strategies.validation.configs import ValidationConfig

# TODO: Split this module into adapters/ once config, event, and session conversions grow larger.


def agent_participant_config_from_create(agent: AgentParticipantCreate) -> AgentParticipantConfig:
    return AgentParticipantConfig(
        name=agent.name,
        model=agent.model,
        system_prompt=agent.system_prompt,
    )


def session_config_from_create(session_create: SessionCreate) -> SessionConfig:
    return SessionConfig(
        prompt=session_create.prompt,
        agents=[agent_participant_config_from_create(agent) for agent in session_create.agents],
        turn_selection=turn_selection_config_from_create(session_create.turn_selection),
        context=context_config_from_create(session_create.context),
        validation=validation_config_from_create(session_create.validation),
        resolution=resolution_config_from_create(session_create.resolution),
    )


def turn_selection_config_from_create(
    turn_selection_create: TurnSelectionConfigCreate,
) -> TurnSelectionConfig:
    return TurnSelectionConfig(mode=turn_selection_create.mode)


def context_config_from_create(context_create: ContextConfigCreate) -> ContextConfig:
    return ContextConfig(mode=context_create.mode)


def validation_config_from_create(validation_create: ValidationConfigCreate) -> ValidationConfig:
    return ValidationConfig(mode=validation_create.mode)


def resolution_config_from_create(
    resolution_create: ResolutionConfigCreate,
) -> JudgeResolutionConfig | NoneResolutionConfig:
    match resolution_create:
        case JudgeResolutionConfigCreate():
            return JudgeResolutionConfig(
                judge_model=resolution_create.judge_model,
                judge_temperature=resolution_create.judge_temperature,
            )
        case NoneResolutionConfigCreate():
            return NoneResolutionConfig()


def participant_read_from_participant(participant: Participant) -> ParticipantRead:
    return ParticipantRead(
        id=participant.id,
        type=participant.type,
        name=participant.name,
        created_at=participant.created_at,
        updated_at=participant.updated_at,
    )


def session_read_from_session(session: Session) -> SessionRead:
    return SessionRead(
        id=session.id,
        prompt=session.prompt,
        created_at=session.created_at,
        updated_at=session.updated_at,
        participants=[participant_read_from_participant(participant) for participant in session.participants],
    )


def session_summary_read_from_summary(summary: SessionSummary) -> SessionSummaryRead:
    return SessionSummaryRead(
        id=summary.id,
        prompt=summary.prompt,
        created_at=summary.created_at,
        updated_at=summary.updated_at,
        participant_count=summary.participant_count,
        status=summary.status,
    )


def event_read_from_event(event: Event) -> EventRead:
    event_fields = _event_fields(event)

    match event:
        case MessageStartedEvent():
            return MessageStartedEventRead(
                **event_fields,
                type=EventType.MESSAGE_STARTED,
                message_id=event.message_id,
                sender=participant_read_from_participant(event.sender),
            )
        case MessageCompletedEvent():
            return MessageCompletedEventRead(
                **event_fields,
                type=EventType.MESSAGE_COMPLETED,
                message_id=event.message_id,
                content=event.content,
            )
        case ParticipantVoteEvent():
            return ParticipantVoteEventRead(
                **event_fields,
                type=EventType.PARTICIPANT_VOTE,
                voter=participant_read_from_participant(event.voter),
                target=participant_read_from_participant(event.target),
                reason=event.reason,
            )
        case ParticipantRemovedEvent():
            return ParticipantRemovedEventRead(
                **event_fields,
                type=EventType.PARTICIPANT_REMOVED,
                removed=participant_read_from_participant(event.removed),
            )
        case ResolutionCreatedEvent():
            return ResolutionCreatedEventRead(
                **event_fields,
                type=EventType.RESOLUTION_CREATED,
                resolution=event.resolution,
            )
        case SessionCompletedEvent():
            return SessionCompletedEventRead(
                **event_fields,
                type=EventType.SESSION_COMPLETED,
            )
        case SessionStartedEvent():
            return SessionStartedEventRead(
                **event_fields,
                type=EventType.SESSION_STARTED,
            )

    raise ValueError(f"Unsupported event type: {event.type}")


def _event_fields(event: Event) -> dict[str, Any]:
    return {
        "id": event.id,
        "session_id": event.session_id,
        "created_at": event.created_at,
        "updated_at": event.updated_at,
    }


def token_read_from_token(token: Token) -> TokenRead:
    return TokenRead(correlation_id=token.correlation_id, content=token.content)
