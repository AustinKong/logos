import tempfile
from datetime import datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlAlchemyDb
from sqlalchemy.orm import selectinload

from api.modules.session_configs.models.participants import ParticipantData
from api.modules.session_configs.models.session_configs import DebateConfig, ProposalConfig, SessionConfig
from api.modules.session_configs.service import SessionConfigService
from api.modules.sessions.errors import SessionNotFoundError
from api.modules.sessions.models.events import (
    AskUserCompletedEvent,
    AskUserStartedEvent,
    DebateRoundCompletedEvent,
    DebateRoundStartedEvent,
    Event,
    MessageCompletedEvent,
    ProposalCompletedEvent,
    ProposalStartedEvent,
    ReasoningCompletedEvent,
    ResolutionCompletedEvent,
    ResolutionStartedEvent,
    SessionCompletedEvent,
    SessionStartedEvent,
    TurnCompletedEvent,
    TurnStartedEvent,
)
from api.modules.sessions.models.sessions import Session, SessionSummary
from api.modules.sessions.repository import SessionRepository
from api.modules.strategies.resolution.configs import ResolutionConfig


class SessionService:
    def __init__(
        self,
        db: SqlAlchemyDb,
        repository: SessionRepository,
        session_config_service: SessionConfigService,
    ) -> None:
        self._db = db
        self._repository = repository
        self._session_config_service = session_config_service

    def create_session(
        self,
        *,
        prompt: str,
        seed: int | None,
        proposal_config: ProposalConfig,
        debate_config: DebateConfig,
        participants: list[ParticipantData],
        resolution_config: ResolutionConfig,
    ) -> Session:
        session_config = self._session_config_service.create_config(
            prompt=prompt,
            seed=seed,
            proposal_config=proposal_config,
            debate_config=debate_config,
            participants=participants,
            resolution_config=resolution_config,
            commit=False,
        )

        session = Session(config_id=session_config.id)
        self._db.add(session)
        self._db.commit()

        return self.get_session(session.id)

    def get_session(self, session_id: UUID) -> Session:
        statement = (
            select(Session)
            .where(Session.id == session_id)
            .options(selectinload(Session.config).selectinload(SessionConfig._participants))
        )
        session = self._db.execute(statement).scalar_one_or_none()
        if session is None:
            raise SessionNotFoundError()

        return session

    def list_session_summaries(self) -> list[SessionSummary]:
        return self._repository.list_session_summaries()

    def list_events(self, session_id: UUID) -> list[Event]:
        self.get_session(session_id)  # Ensure session exists
        return self._repository.list_events(session_id)

    def export_session(self, session_id: UUID) -> Path:
        session = self.get_session(session_id)
        events = self._repository.list_events(session_id)
        export_path = Path(tempfile.gettempdir()) / f"logos-session-{session_id}.md"
        export_path.write_text(_format_session_export(session, events), encoding="utf-8")
        return export_path

    def list_events_after(self, session_id: UUID, created_at: datetime) -> list[Event]:
        self.get_session(session_id)
        return self._repository.list_events_after(session_id, created_at)

    def append_events(self, session_id: UUID, events: list[Event]) -> list[Event]:
        self.get_session(session_id)

        for event in events:
            event.session_id = session_id

        self._db.add_all(events)
        self._db.commit()
        return events


# TODO: Handle this better
def _format_session_export(session: Session, events: list[Event]) -> str:
    lines = [
        f"# Session {session.id}",
        "",
        "## Prompt",
        "",
        session.config.prompt,
        "",
        "## Transcript",
        "",
    ]
    turn_sender: str | None = None

    for event in events:
        match event:
            case TurnStartedEvent():
                turn_sender = event.sender.name
            case TurnCompletedEvent():
                turn_sender = None
            case AskUserStartedEvent():
                lines.extend([f"### {turn_sender or 'Unknown'} asks user", "", event.question, ""])
            case AskUserCompletedEvent():
                lines.extend(["Answer:", "", event.answer, ""])
            case MessageCompletedEvent():
                lines.extend([f"### {turn_sender or 'Unknown'}", "", event.content, ""])
            case ReasoningCompletedEvent():
                lines.extend([f"### {turn_sender or 'Unknown'} reasoning", "", event.content, ""])
            case SessionStartedEvent():
                lines.extend(["Session started.", ""])
            case SessionCompletedEvent():
                lines.extend(["Session completed.", ""])
            case ProposalStartedEvent():
                lines.extend(["## Proposal", ""])
            case ProposalCompletedEvent():
                pass
            case DebateRoundStartedEvent():
                lines.extend([f"## Debate round {event.round_number}", ""])
            case DebateRoundCompletedEvent():
                pass
            case ResolutionStartedEvent():
                lines.extend(["## Resolution", ""])
            case ResolutionCompletedEvent():
                lines.extend([event.decision, ""])
            case _:
                pass

    return "\n".join(lines).strip() + "\n"
