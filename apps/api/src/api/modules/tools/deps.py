from typing import Annotated

from fastapi import Depends

from api.modules.tools.ask_user.deps import get_ask_user_service
from api.modules.tools.ask_user.service import AskUserService
from api.modules.tools.resolver import ToolResolver
from api.modules.tools.service import ToolService


def get_tool_resolver(
    ask_user_service: Annotated[AskUserService, Depends(get_ask_user_service)],
) -> ToolResolver:
    return ToolResolver(
        ask_user_service=ask_user_service,
    )


def get_tool_service(
    resolver: Annotated[ToolResolver, Depends(get_tool_resolver)],
) -> ToolService:
    return ToolService(resolver=resolver)
