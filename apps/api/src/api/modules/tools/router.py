from typing import Annotated

from fastapi import APIRouter, Depends

from api.modules.tools.adapters import tool_read_from_definition
from api.modules.tools.ask_user.router import router as ask_user_router
from api.modules.tools.deps import get_tool_service
from api.modules.tools.models import ToolScope
from api.modules.tools.schemas import ToolRead
from api.modules.tools.service import ToolService

router = APIRouter(prefix="/tools", tags=["tools"])
router.include_router(ask_user_router)


@router.get("", operation_id="listAvailableTools", response_model=list[ToolRead])
def list_available_tools(
    scope: ToolScope,
    service: Annotated[ToolService, Depends(get_tool_service)],
) -> list[ToolRead]:
    return [tool_read_from_definition(tool) for tool in service.list_available_tools(scope=scope)]
