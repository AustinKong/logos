from api_client.models import ToolRead
from textual.widgets import SelectionList


class ToolsSelect(SelectionList[str]):
    DEFAULT_CSS = """
    ToolsSelect {
        width: 100%;
        height: auto;
    }
    """

    def __init__(
        self,
        *,
        tools: list[ToolRead],
        initial_values: list[str],
        read_only: bool = False,
    ) -> None:
        super().__init__(
            *((f"{tool.title}: {tool.description}", tool.name, tool.name in initial_values) for tool in tools),
            disabled=read_only,
            compact=True,
        )

    def form_state(self) -> list[str]:
        return self.selected
