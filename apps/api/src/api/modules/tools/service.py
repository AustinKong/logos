from collections.abc import Sequence

from api.modules.tools.base import Tool
from api.modules.tools.models import ToolDefinition, ToolScope
from api.modules.tools.resolver import ToolResolver


class ToolService:
    def __init__(
        self,
        *,
        resolver: ToolResolver,
    ) -> None:
        self._resolver = resolver

    def list_available_tools(self, *, scope: ToolScope) -> list[ToolDefinition]:
        return self._resolver.list_available_tools(scope=scope)

    def resolve_tools(self, names: Sequence[str], *, scope: ToolScope) -> list[Tool]:
        return self._resolver.get_tools(names, scope=scope)
