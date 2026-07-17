from typing import Annotated

from fastapi import Depends

from api.deps import DbDep
from api.modules.ai.deps import get_ai_service
from api.modules.ai.service import AIService
from api.modules.session_configs.service import SessionConfigService
from api.modules.tools.deps import get_tool_service
from api.modules.tools.service import ToolService


def get_session_config_service(
    db: DbDep,
    ai_service: Annotated[AIService, Depends(get_ai_service)],
    tool_service: Annotated[ToolService, Depends(get_tool_service)],
) -> SessionConfigService:
    return SessionConfigService(db=db, ai_service=ai_service, tool_service=tool_service)
