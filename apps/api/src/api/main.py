from fastapi import FastAPI

from api.modules.health.router import router as health_router
from api.modules.sessions.router import router as sessions_router
from api.settings import get_settings
from api.shared.errors import AppError
from api.shared.exception_handlers import app_error_handler


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(health_router)
    app.include_router(sessions_router)
    return app


app = create_app()
