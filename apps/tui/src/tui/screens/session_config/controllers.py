from api_client import Client
from api_client.api.session_drafts.generate_session_draft_participants import (
    asyncio as generate_session_draft_participants,
)
from api_client.api.session_drafts.get_session_draft_defaults import asyncio as get_session_draft_defaults
from api_client.api.sessions.create_session import asyncio as create_session
from api_client.models import (
    AgentParticipantCreate,
    GenerateParticipantsRequest,
    GenerateParticipantsResponse,
    SessionCreate,
    SessionDraftDefaultsRead,
    SessionRead,
)


class SessionConfigController:
    def __init__(self, *, client: Client) -> None:
        self._client = client

    async def create_session(self, draft: SessionCreate) -> SessionRead:
        session = await create_session(client=self._client, body=draft)
        if not isinstance(session, SessionRead):
            raise RuntimeError("API returned an unexpected create session response")

        return session

    async def get_draft_defaults(self) -> SessionDraftDefaultsRead:
        defaults = await get_session_draft_defaults(client=self._client)
        if not isinstance(defaults, SessionDraftDefaultsRead):
            raise RuntimeError("API returned an unexpected session draft defaults response")

        return defaults

    async def generate_participants(self, *, prompt: str) -> list[AgentParticipantCreate]:
        response = await generate_session_draft_participants(
            client=self._client,
            body=GenerateParticipantsRequest(prompt=prompt),
        )
        if not isinstance(response, GenerateParticipantsResponse):
            raise RuntimeError("API returned an unexpected participant generation response")

        return response.agents
