from api.modules.session_configs.adapters.session_configs import session_config_read_from_config
from api.modules.sessions.models.sessions import Session, SessionSummary
from api.modules.sessions.schemas.sessions import SessionRead, SessionSummaryRead


def session_read_from_session(session: Session) -> SessionRead:
    return SessionRead(
        id=session.id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        config=session_config_read_from_config(session.config),
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
