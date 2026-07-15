from collections.abc import Sequence

from api.modules.tools.ask_user.service import AskUserService
from api.modules.tools.ask_user.tool import AskUserTool
from api.modules.tools.base import Tool
from api.modules.tools.errors import UnknownToolError


class ToolResolver:
    def __init__(
        self,
        *,
        ask_user_service: AskUserService,
    ) -> None:
        self._ask_user_service = ask_user_service

    def get_tools(self, names: Sequence[str]) -> list[Tool]:
        tools: list[Tool] = []
        for name in names:
            match name:
                case AskUserTool.name:
                    tools.append(AskUserTool(ask_user_service=self._ask_user_service))
                case _:
                    raise UnknownToolError(f"Unknown tool: {name}")

        return tools
