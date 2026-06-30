from api_client import Client
from textual.app import App
from textual.binding import Binding

from tui.navigation import Navigate, Navigator, Route
from tui.settings import Settings, get_settings
from tui.shared.textual import on


class TuiApp(App[None]):
    TITLE = "Logos"
    SUB_TITLE = "Terminal workspace"
    BINDINGS = [Binding("ctrl+q", "quit", "Quit", key_display="Ctrl+Q")]
    CSS_PATH = "app.tcss"

    def __init__(self, *, settings: Settings | None = None) -> None:
        super().__init__()
        self._settings = settings or get_settings()
        self._api_client = Client(base_url=self._settings.api_base_url, raise_on_unexpected_status=True)
        self._navigator = Navigator(app=self, client=self._api_client)

    async def on_mount(self) -> None:
        await self._api_client.__aenter__()
        self._navigator.navigate(Route.SESSIONS)

    async def on_unmount(self) -> None:
        await self._api_client.__aexit__(None, None, None)

    @on(Navigate)
    def handle_navigate(self, message: Navigate) -> None:
        self._navigator.navigate(message.route, message.params)
