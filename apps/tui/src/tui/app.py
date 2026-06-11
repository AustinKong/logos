import os

from api_client import Client
from api_client.api.health import get_health
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Footer, Header, Static


class TuiApp(App[None]):
    TITLE = "Logos"
    SUB_TITLE = "Terminal workspace"
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, *, api_base_url: str | None = None, fetch_health: bool = True) -> None:
        super().__init__()
        self.api_base_url = api_base_url or os.getenv("TUI_API_BASE_URL", "http://127.0.0.1:8000")
        self.fetch_health = fetch_health

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("Logos", id="title"),
            Static("Checking API health...", id="status"),
            id="home",
        )
        yield Footer()

    async def on_mount(self) -> None:
        if not self.fetch_health:
            return

        status = self.query_one("#status", Static)
        status.update(await self.load_health_status())

    async def load_health_status(self) -> str:
        try:
            async with Client(base_url=self.api_base_url) as client:
                response = await get_health.asyncio(client=client)
        except Exception as exc:
            return f"API health: error ({exc})"

        if response is None:
            return "API health: unexpected response"

        return f"API health: {response.status}"
