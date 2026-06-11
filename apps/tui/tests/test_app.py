import pytest
from api_client.models import HealthCheckResponse
from textual.widgets import Static
from tui import app as tui_app
from tui.app import TuiApp


@pytest.mark.anyio
async def test_app_mounts_home_screen() -> None:
    app = TuiApp(fetch_health=False)

    async with app.run_test() as pilot:
        title = pilot.app.query_one("#title", Static)
        status = pilot.app.query_one("#status", Static)

    assert title.id == "title"
    assert status.id == "status"


@pytest.mark.anyio
async def test_app_loads_health_status(monkeypatch: pytest.MonkeyPatch) -> None:
    async def mock_get_health(*, client: object) -> HealthCheckResponse:
        return HealthCheckResponse(status="ok")

    monkeypatch.setattr(tui_app.get_health, "asyncio", mock_get_health)

    app = TuiApp()

    assert await app.load_health_status() == "API health: ok"
