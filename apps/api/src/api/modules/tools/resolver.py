from api.modules.ai.models import AIToolDefinition
from api.modules.tools.ask_user.service import AskUserService
from api.modules.tools.ask_user.tool import AskUserTool
from api.modules.tools.base import Tool
from api.modules.tools.errors import UnknownToolError


class ToolResolver:
    # TODO: Since we might not need list definitions anymore, maybe a match case?
    # Altho better would be to have an enum for tool names.
    # Callers can use this enum to specify which tools they can supply during generation step
    # Then we dont need list definitions, we can just use the enum
    # And resolve can jst be a match case on enum value. then non need tools and tools by name in constructor
    def __init__(
        self,
        *,
        ask_user_service: AskUserService,
    ) -> None:
        tools: list[Tool] = [
            AskUserTool(
                ask_user_service=ask_user_service,
            ),
        ]
        self._tools_by_name = {tool.definition.name: tool for tool in tools}

    def resolve(self, name: str) -> Tool:
        try:
            return self._tools_by_name[name]
        except KeyError as exc:
            raise UnknownToolError(f"AI provider requested an unknown tool: {name}") from exc

    def list_definitions(self) -> list[AIToolDefinition]:
        return [tool.definition for tool in self._tools_by_name.values()]
