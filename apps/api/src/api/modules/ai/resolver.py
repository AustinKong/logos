from typing import assert_never

from api.modules.ai.errors import AIProviderMismatchError, UnsupportedEmbeddingModelError, UnsupportedLanguageModelError
from api.modules.ai.models import AIEmbeddingModel, AILanguageModel, AIProviderName
from api.modules.ai.providers.anthropic import AnthropicProvider
from api.modules.ai.providers.base import AIProvider
from api.modules.ai.providers.deepseek import DeepSeekProvider
from api.modules.ai.providers.gemini import GeminiProvider
from api.modules.ai.providers.openai import OpenAIProvider
from api.settings import Settings


class AIProviderResolver:
    def __init__(self, *, settings: Settings) -> None:
        self._settings = settings

    def list_available_language_models(self) -> list[AILanguageModel]:
        return [model for provider in self._configured_providers() for model in provider.list_language_models()]

    def list_available_embedding_models(self) -> list[AIEmbeddingModel]:
        return [model for provider in self._configured_providers() for model in provider.list_embedding_models()]

    def resolve_language_model(self, model: str) -> AIProvider:
        provider = self._provider_for(_parse_model_provider(model))
        if not any(language_model.id == model for language_model in provider.list_language_models()):
            raise UnsupportedLanguageModelError()

        return provider

    def resolve_embedding_model(self, model: str) -> AIProvider:
        provider = self._provider_for(_parse_model_provider(model))
        if not any(embedding_model.id == model for embedding_model in provider.list_embedding_models()):
            raise UnsupportedEmbeddingModelError()

        return provider

    def _configured_providers(self) -> list[AIProvider]:
        providers: list[AIProvider] = []
        for provider_name in AIProviderName:
            try:
                providers.append(self._provider_for(provider_name))
            except AIProviderMismatchError:
                continue

        return providers

    def _provider_for(self, provider: AIProviderName) -> AIProvider:
        api_key = self._get_api_key(provider=provider)
        match provider:
            case AIProviderName.OPENAI:
                return OpenAIProvider(api_key)
            case AIProviderName.ANTHROPIC:
                return AnthropicProvider(api_key)
            case AIProviderName.GEMINI:
                return GeminiProvider(api_key)
            case AIProviderName.DEEPSEEK:
                return DeepSeekProvider(api_key)
            case _ as never:
                assert_never(never)

    def _get_api_key(self, provider: AIProviderName) -> str:
        api_keys = self._settings.ai.api_keys
        match provider:
            case AIProviderName.OPENAI:
                api_key = api_keys.openai
            case AIProviderName.ANTHROPIC:
                api_key = api_keys.anthropic
            case AIProviderName.GEMINI:
                api_key = api_keys.gemini
            case AIProviderName.DEEPSEEK:
                api_key = api_keys.deepseek
            case _ as never:
                assert_never(never)

        if not api_key:
            raise AIProviderMismatchError(f"AI provider API key is not configured for provider: {provider.value}")

        return api_key


def _parse_model_provider(model: str) -> AIProviderName:
    provider = model.split("/", maxsplit=1)[0]
    try:
        return AIProviderName(provider)
    except ValueError as exc:
        raise AIProviderMismatchError(f"AI model provider is not supported: {provider}") from exc
