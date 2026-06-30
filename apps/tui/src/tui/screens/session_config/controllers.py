from uuid import UUID

from api_client import Client
from api_client.api.ai.list_ai_models import asyncio as list_ai_models_api
from api_client.api.session_configs.get_default_session_config import asyncio as get_default_session_config
from api_client.api.sessions.create_session import asyncio as create_session_api
from api_client.api.sessions.get_session import asyncio as get_session
from api_client.models import AIModelRead, SessionConfigRead, SessionRead

from tui.screens.session_config.adapters import session_create_from_form_state
from tui.screens.session_config.models import SessionConfigFormState


class SessionConfigController:
    def __init__(self, *, client: Client) -> None:
        self._client = client

    async def create_session(self, form_state: SessionConfigFormState) -> SessionRead:
        session = await create_session_api(client=self._client, body=session_create_from_form_state(form_state))
        if not isinstance(session, SessionRead):
            raise RuntimeError("API returned an unexpected create session response")

        return session

    async def get_default_config(self) -> SessionConfigRead:
        config = await get_default_session_config(client=self._client)
        if not isinstance(config, SessionConfigRead):
            raise RuntimeError("API returned an unexpected default session config response")

        return config

    async def list_ai_models(self) -> list[AIModelRead]:
        models = await list_ai_models_api(client=self._client)
        if not isinstance(models, list):
            raise RuntimeError("API returned an unexpected AI models response")

        return models

    async def get_session(self, *, session_id: UUID) -> SessionRead:
        session = await get_session(session_id, client=self._client)
        if not isinstance(session, SessionRead):
            raise RuntimeError("API returned an unexpected session response")

        return session
