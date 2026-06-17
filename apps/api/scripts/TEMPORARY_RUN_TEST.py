import asyncio

from api.db.models import Base
from api.modules.ai.resolver import AIProviderResolver
from api.modules.ai.service import AIService
from api.modules.engine.engine import Engine
from api.modules.engine.service import EngineService
from api.modules.sessions.models.events import (
    ParticipantMessageEvent,
    ResolutionCreatedEvent,
    SessionCompletedEvent,
    SessionStartedEvent,
)
from api.modules.sessions.models.participants import AgentParticipantConfig
from api.modules.sessions.repository import SessionRepository
from api.modules.sessions.service import SessionService
from api.settings import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

MODEL = "openai/gpt-4o-mini"


async def main() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    db_factory = sessionmaker(bind=engine, expire_on_commit=False)
    with db_factory() as db:
        session_service = SessionService(db, SessionRepository(db))
        ai_service = AIService(
            AIProviderResolver(
                settings=get_settings(),
            )
        )
        engine_service = EngineService(
            session_service=session_service,
            engine=Engine(ai_service),
        )

        session = session_service.create_session(
            prompt="How should engineering teams decide when to use AI agents in production workflows?",
            agents=[
                AgentParticipantConfig(
                    name="Pragmatist",
                    model=MODEL,
                    system_prompt="Argue for the simplest useful implementation that proves value quickly.",
                ),
                AgentParticipantConfig(
                    name="Skeptic",
                    model=MODEL,
                    system_prompt="Point out risks, failure modes, and missing safeguards in the implementation.",
                ),
            ],
        )

        emitted_events = await engine_service.run_until_blocked(session.id)

        print(f"session_id={session.id}")
        print(f"emitted_events={len(emitted_events)}")
        for event in emitted_events:
            if isinstance(event, SessionStartedEvent):
                print(f"- {event.type}")
            elif isinstance(event, ResolutionCreatedEvent):
                print(f"- {event.type} resolution={event.resolution!r}")
            elif isinstance(event, SessionCompletedEvent):
                print(f"- {event.type}")
            elif isinstance(event, ParticipantMessageEvent):
                print(f"- {event.type} sender_id={event.sender_id} content={event.content!r}")
            else:
                print(f"- {event.type}")


if __name__ == "__main__":
    asyncio.run(main())
