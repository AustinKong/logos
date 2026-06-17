from api_client import Client
from textual.app import App

from tui.screens.session.controllers import SessionController
from tui.screens.session.loaders import SessionLoader
from tui.screens.session.screen import SessionScreen
from tui.settings import Settings, get_settings


class TuiApp(App[None]):
    TITLE = "Logos"
    SUB_TITLE = "Terminal workspace"
    BINDINGS = [("q", "quit", "Quit")]

    def __init__(self, *, settings: Settings | None = None) -> None:
        super().__init__()
        self._settings = settings or get_settings()
        self._api_client = Client(base_url=self._settings.api_base_url, raise_on_unexpected_status=True)

    async def on_mount(self) -> None:
        await self._api_client.__aenter__()
        self.push_screen(
            SessionScreen(
                controller=SessionController(client=self._api_client),
                loader=SessionLoader(client=self._api_client),
            )
        )

    async def on_unmount(self) -> None:
        await self._api_client.__aexit__(None, None, None)
