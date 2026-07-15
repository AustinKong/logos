from api.modules.tools.base import Tool
from api.modules.tools.schemas import ToolRead


def tool_read_from_tool(tool: Tool) -> ToolRead:
    return ToolRead(
        name=tool.name,
        title=tool.title,
        description=tool.definition.description,
    )
