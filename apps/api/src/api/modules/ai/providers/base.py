from collections.abc import AsyncIterable, Sequence
from typing import Protocol, TypeVar

from pydantic import BaseModel

from api.modules.ai.models import AIMessage, GenerationOptions

# Bind to BaseModel because we use model_validate_json
GeneratedObject = TypeVar("GeneratedObject", bound=BaseModel)


class AIProvider(Protocol):
    async def generate_text(self, *, messages: Sequence[AIMessage], options: GenerationOptions) -> str: ...

    async def stream_text(self, *, messages: Sequence[AIMessage], options: GenerationOptions) -> AsyncIterable[str]: ...

    async def generate_object(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
        response_model: type[GeneratedObject],
    ) -> GeneratedObject: ...
