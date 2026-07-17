from uuid import UUID

from api_client import Client
from api_client.api.tools.answer_ask_user import asyncio as answer_ask_user
from api_client.models import AskUserAnswerKind, AskUserAnswerRequest, AskUserCompletedEventRead


class AskUserController:
    def __init__(self, *, client: Client) -> None:
        self._client = client

    async def answer(
        self,
        *,
        ask_user_id: UUID,
        answer_kind: AskUserAnswerKind,
        answer: str,
    ) -> AskUserCompletedEventRead:
        response = await answer_ask_user(
            ask_user_id,
            client=self._client,
            body=AskUserAnswerRequest(answer_kind=answer_kind, answer=answer),
        )
        if not isinstance(response, AskUserCompletedEventRead):
            raise RuntimeError("API returned an unexpected answer ask-user response")

        return response
