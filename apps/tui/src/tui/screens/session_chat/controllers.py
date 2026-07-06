from uuid import UUID

from api_client import Client
from api_client.api.sessions.export_session import asyncio as export_session
from api_client.models import SessionExportResponse


class SessionChatController:
    def __init__(self, *, client: Client) -> None:
        self._client = client

    async def export_session(self, *, session_id: UUID) -> str:
        response = await export_session(session_id, client=self._client)
        if not isinstance(response, SessionExportResponse):
            raise RuntimeError("API returned an unexpected export session response")

        return response.path
