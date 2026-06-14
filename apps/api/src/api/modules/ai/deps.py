from typing import Annotated

from fastapi import Depends

from api.modules.ai.resolver import AIProviderResolver
from api.modules.ai.service import AIService
from api.settings import Settings, get_settings


def get_ai_provider_resolver(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AIProviderResolver:
    return AIProviderResolver(settings=settings)


def get_ai_service(provider_resolver: Annotated[AIProviderResolver, Depends(get_ai_provider_resolver)]) -> AIService:
    return AIService(provider_resolver=provider_resolver)
