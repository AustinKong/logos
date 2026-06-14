from api.modules.ai.errors import AIProviderMismatchError
from api.modules.ai.models import AIProviderPrefix
from api.modules.ai.providers.base import AIProvider
from api.modules.ai.providers.litellm import LiteLLMProvider
from api.settings import Settings


class AIProviderResolver:
    def __init__(self, *, settings: Settings) -> None:
        self._settings = settings

    def resolve(self, model: str) -> AIProvider:
        prefix = _parse_model_prefix(model)
        api_keys = self._settings.ai.api_keys
        # In future (if/when we drop LiteLLM), route to different providers based on prefix here.
        match prefix:
            case AIProviderPrefix.OPENAI:
                return LiteLLMProvider(_get_api_key(prefix=prefix, api_key=api_keys.openai))
            case AIProviderPrefix.ANTHROPIC:
                return LiteLLMProvider(_get_api_key(prefix=prefix, api_key=api_keys.anthropic))
            case AIProviderPrefix.GEMINI:
                return LiteLLMProvider(_get_api_key(prefix=prefix, api_key=api_keys.gemini))
            case AIProviderPrefix.DEEPSEEK:
                return LiteLLMProvider(_get_api_key(prefix=prefix, api_key=api_keys.deepseek))


def _parse_model_prefix(model: str) -> AIProviderPrefix:
    prefix = model.split("/", maxsplit=1)[0]
    try:
        return AIProviderPrefix(prefix)
    except ValueError as exc:
        raise AIProviderMismatchError(f"AI model provider prefix is not supported: {prefix}") from exc


def _get_api_key(*, prefix: AIProviderPrefix, api_key: str | None) -> str:
    if not api_key:
        raise AIProviderMismatchError(f"AI provider API key is not configured for model prefix: {prefix.value}")
    return api_key
