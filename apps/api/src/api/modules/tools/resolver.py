from collections.abc import Sequence

from api.modules.tools.ask_user.definition import ASK_USER_TOOL_DEFINITION
from api.modules.tools.ask_user.service import AskUserService
from api.modules.tools.ask_user.tool import AskUserTool
from api.modules.tools.base import Tool
from api.modules.tools.errors import ToolUnavailableError, UnknownToolError
from api.modules.tools.models import ToolDefinition, ToolScope


class ToolResolver:
    def __init__(
        self,
        *,
        ask_user_service: AskUserService,
    ) -> None:
        self._ask_user_service = ask_user_service

    def list_available_tools(self, *, scope: ToolScope) -> list[ToolDefinition]:
        return [tool.definition for tool in self._all_tools() if scope in tool.definition.scopes]

    def get_tools(self, names: Sequence[str], *, scope: ToolScope) -> list[Tool]:
        tools: list[Tool] = []
        for name in names:
            tool = self._tool_for(name)
            if scope not in tool.definition.scopes:
                raise ToolUnavailableError(f"Tool is unavailable for {scope.value}: {tool.definition.name}")
            tools.append(tool)

        return tools

    def _tool_for(self, name: str) -> Tool:
        match name:
            case _ if name == ASK_USER_TOOL_DEFINITION.name:
                return AskUserTool(ask_user_service=self._ask_user_service)
            case _:
                raise UnknownToolError(f"Unknown tool: {name}")

    def _all_tools(self) -> list[Tool]:
        return [self._tool_for(ASK_USER_TOOL_DEFINITION.name)]
