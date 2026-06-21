from api_client import Client
from api_client.api.sessions.list_sessions import asyncio as list_sessions
from api_client.models.session_summary_read import SessionSummaryRead


class SessionsLoader:
    def __init__(self, *, client: Client) -> None:
        self._client = client

    async def list_sessions(self) -> list[SessionSummaryRead]:
        sessions = await list_sessions(client=self._client)
        if not isinstance(sessions, list):
            raise RuntimeError("API returned an unexpected list sessions response")

        return sessions
