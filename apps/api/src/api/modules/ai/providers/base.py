from abc import ABC, abstractmethod
from collections.abc import AsyncIterable, Sequence
from typing import TypeVar

from pydantic import BaseModel

from api.modules.ai.models import AIMessage, GenerationOptions

GeneratedObject = TypeVar("GeneratedObject", bound=BaseModel)


class AIProvider(ABC):
    @abstractmethod
    async def generate_text(self, *, messages: Sequence[AIMessage], options: GenerationOptions) -> str:
        pass

    @abstractmethod
    async def stream_text(self, *, messages: Sequence[AIMessage], options: GenerationOptions) -> AsyncIterable[str]:
        pass

    @abstractmethod
    async def generate_object(
        self,
        *,
        messages: Sequence[AIMessage],
        options: GenerationOptions,
        response_model: type[GeneratedObject],
    ) -> GeneratedObject:
        pass
