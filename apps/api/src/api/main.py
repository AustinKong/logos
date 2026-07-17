from fastapi import FastAPI

from api.modules.ai.router import router as ai_router
from api.modules.health.router import router as health_router
from api.modules.session_configs.router import router as session_configs_router
from api.modules.sessions.router import router as sessions_router
from api.modules.tools.router import router as tools_router
from api.settings import get_settings
from api.shared.errors import AppError
from api.shared.exception_handlers import app_error_handler


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(ai_router)
    app.include_router(health_router)
    app.include_router(session_configs_router)
    app.include_router(sessions_router)
    app.include_router(tools_router)
    return app


app = create_app()
