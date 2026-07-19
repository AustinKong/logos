from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.session_configs.models.participants import Participant, ParticipantType
from api.modules.session_configs.models.session_configs import SessionConfig
from api.modules.sessions.models.events import Event
from api.modules.sessions.models.sessions import Session, SessionStatus, SessionSummary


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_session_summaries(self) -> list[SessionSummary]:
        statement = (
            select(
                Session.id,
                SessionConfig.prompt,
                Session.created_at,
                Session.updated_at,
                func.count(distinct(Participant.id)),
                func.count(distinct(Event.id)),
            )
            .join(SessionConfig, SessionConfig.id == Session.config_id)
            .outerjoin(
                Participant,
                and_(
                    Participant.config_id == SessionConfig.id,
                    Participant.type == ParticipantType.DEBATER,
                ),
            )
            .outerjoin(Event, Event.session_id == Session.id)
            .group_by(Session.id, SessionConfig.prompt)
            .order_by(Session.updated_at.desc(), Session.id.desc())
        )
        result = await self._db.execute(statement)
        return [
            SessionSummary(
                id=row.id,
                prompt=row.prompt,
                created_at=row.created_at,
                updated_at=row.updated_at,
                participant_count=row[4],
                status=SessionStatus.from_has_events(has_events=bool(row[5])),
            )
            for row in result
        ]

    async def list_events(self, session_id: UUID) -> list[Event]:
        statement = select(Event).where(Event.session_id == session_id).order_by(Event.created_at, Event.id)
        result = await self._db.execute(statement)
        return list(result.scalars())

    async def list_events_after(self, session_id: UUID, created_at: datetime) -> list[Event]:
        statement = (
            select(Event)
            .where(Event.session_id == session_id)
            .where(Event.created_at > created_at)
            .order_by(Event.created_at, Event.id)
        )
        result = await self._db.execute(statement)
        return list(result.scalars())
