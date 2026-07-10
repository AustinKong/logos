from typing import Annotated

from fastapi import Depends

from api.modules.tools.ask_user.deps import get_ask_user_service
from api.modules.tools.ask_user.service import AskUserService
from api.modules.tools.resolver import ToolResolver


def get_tool_resolver(
    ask_user_service: Annotated[AskUserService, Depends(get_ask_user_service)],
) -> ToolResolver:
    return ToolResolver(
        ask_user_service=ask_user_service,
    )
