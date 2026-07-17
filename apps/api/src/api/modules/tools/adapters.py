from api.modules.ai.models import AIToolDefinition
from api.modules.tools.models import ToolDefinition
from api.modules.tools.schemas import ToolRead


def tool_read_from_definition(tool: ToolDefinition) -> ToolRead:
    return ToolRead(
        name=tool.name,
        title=tool.title,
        description=tool.user_description,
    )


def ai_tool_definition_from_definition(tool: ToolDefinition) -> AIToolDefinition:
    return AIToolDefinition(
        name=tool.name,
        description=tool.ai_description,
        parameters=tool.parameters,
    )
