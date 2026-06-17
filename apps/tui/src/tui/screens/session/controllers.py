from api_client import Client
from api_client.api.sessions.create_session import asyncio as create_session
from api_client.api.sessions.run_session_until_blocked import asyncio_detailed as run_session_until_blocked
from api_client.models.session_create import SessionCreate
from api_client.models.session_read import SessionRead


class SessionController:
    def __init__(self, *, client: Client) -> None:
        self._client = client

    async def create_and_start_session(self, *, prompt: str) -> SessionRead:
        response = await create_session(client=self._client, body=SessionCreate(prompt=prompt))

        if not isinstance(response, SessionRead):
            raise RuntimeError("API returned an unexpected create session response")

        run_response = await run_session_until_blocked(response.id, client=self._client)
        if run_response.status_code != 202:
            raise RuntimeError("API returned an unexpected run session response")

        return response
