from uuid import UUID

from api.db.database import db_context
from api.modules.ai.resolver import AIProviderResolver
from api.modules.ai.service import AIService
from api.modules.engine.engine import Engine
from api.modules.engine.service import EngineService
from api.modules.sessions.repository import SessionRepository
from api.modules.sessions.service import SessionService
from api.modules.streaming.deps import get_streaming_service
from api.settings import get_settings


async def run_session_until_blocked_background(session_id: UUID) -> None:
    with db_context() as db:
        session_service = SessionService(db, SessionRepository(db))
        ai_service = AIService(AIProviderResolver(settings=get_settings()))
        engine_service = EngineService(
            session_service=session_service,
            engine=Engine(ai_service),
            streaming_service=get_streaming_service(),
        )
        await engine_service.run_until_blocked(session_id)
