from api.modules.ai.errors import AIProviderMismatchError
from api.modules.ai.models import AIProviderPrefix
from api.modules.ai.providers.base import AIProvider
from api.settings import Settings


class AIProviderResolver:
    def __init__(self, *, litellm_provider: AIProvider, settings: Settings) -> None:
        self._litellm_provider = litellm_provider
        self._settings = settings

    def resolve(self, model: str) -> AIProvider:
        prefix = _parse_model_prefix(model)
        api_keys = self._settings.ai.api_keys
        # In future (if/when we drop LiteLLM), route to different providers based on prefix here.
        match prefix:
            case AIProviderPrefix.OPENAI:
                _require_api_key(prefix=prefix, api_key=api_keys.openai)
                return self._litellm_provider
            case AIProviderPrefix.ANTHROPIC:
                _require_api_key(prefix=prefix, api_key=api_keys.anthropic)
                return self._litellm_provider
            case AIProviderPrefix.GEMINI:
                _require_api_key(prefix=prefix, api_key=api_keys.gemini)
                return self._litellm_provider
            case AIProviderPrefix.DEEPSEEK:
                _require_api_key(prefix=prefix, api_key=api_keys.deepseek)
                return self._litellm_provider


def _parse_model_prefix(model: str) -> AIProviderPrefix:
    prefix = model.split("/", maxsplit=1)[0]
    try:
        return AIProviderPrefix(prefix)
    except ValueError as exc:
        raise AIProviderMismatchError(f"AI model provider prefix is not supported: {prefix}") from exc


def _require_api_key(*, prefix: AIProviderPrefix, api_key: str | None) -> None:
    if not api_key:
        raise AIProviderMismatchError(f"AI provider API key is not configured for model prefix: {prefix.value}")
