from uuid import UUID

from api.db.database import db_context
from api.modules.ai.resolver import AIProviderResolver
from api.modules.ai.service import AIService
from api.modules.engine.engine import Engine
from api.modules.engine.generation import GenerationRunner
from api.modules.engine.service import EngineService
from api.modules.session_configs.service import SessionConfigService
from api.modules.sessions.repository import SessionRepository
from api.modules.sessions.service import SessionService
from api.modules.strategies.resolver import StrategyResolver
from api.modules.streaming.deps import get_streaming_service
from api.modules.tools.ask_user.cache import AskUserCacheRepository
from api.modules.tools.ask_user.service import AskUserService
from api.modules.tools.resolver import ToolResolver
from api.settings import get_settings
from api.vector.database import get_vector_db


async def run_session_until_blocked_background(session_id: UUID) -> None:
    with db_context() as db:
        settings = get_settings()
        ai_service = AIService(provider_resolver=AIProviderResolver(settings=settings), settings=settings)
        session_config_service = SessionConfigService(db=db, ai_service=ai_service)
        session_service = SessionService(db, SessionRepository(db), session_config_service)
        ask_user_cache_repository = AskUserCacheRepository(vector_db=get_vector_db())
        ask_user_service = AskUserService(
            db=db,
            session_service=session_service,
            ai_service=ai_service,
            cache_repository=ask_user_cache_repository,
        )
        strategy_resolver = StrategyResolver(ai_service=ai_service)
        tool_resolver = ToolResolver(
            ask_user_service=ask_user_service,
        )
        generation_runner = GenerationRunner(ai_service=ai_service)
        engine_service = EngineService(
            session_service=session_service,
            engine=Engine(
                generation_runner=generation_runner,
                strategy_resolver=strategy_resolver,
                tool_resolver=tool_resolver,
            ),
            streaming_service=get_streaming_service(),
        )
        await engine_service.run_until_blocked(session_id)
