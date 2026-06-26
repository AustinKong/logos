from api.modules.ai.catalog import AI_MODEL_CATALOG
from api.modules.ai.errors import AIProviderMismatchError
from api.modules.ai.models import AIModel, AIProviderName
from api.modules.ai.providers.base import AIProvider
from api.modules.ai.providers.litellm import LiteLLMProvider
from api.settings import Settings


class AIProviderResolver:
    def __init__(self, *, settings: Settings) -> None:
        self._settings = settings

    def resolve(self, model: str) -> AIProvider:
        prefix = _parse_model_prefix(model)
        # In future (if/when we drop LiteLLM), route to different providers based on prefix here.
        return LiteLLMProvider(self._get_api_key(prefix=prefix))

    def list_available_models(self) -> list[AIModel]:
        available: list[AIModel] = []
        for model in AI_MODEL_CATALOG:
            try:
                self._get_api_key(prefix=model.provider)
            except AIProviderMismatchError:
                continue

            available.append(model)

        return available

    def _get_api_key(self, prefix: AIProviderName) -> str:
        api_keys = self._settings.ai.api_keys
        match prefix:
            case AIProviderName.OPENAI:
                api_key = api_keys.openai
            case AIProviderName.ANTHROPIC:
                api_key = api_keys.anthropic
            case AIProviderName.GEMINI:
                api_key = api_keys.gemini
            case AIProviderName.DEEPSEEK:
                api_key = api_keys.deepseek

        if not api_key:
            raise AIProviderMismatchError(f"AI provider API key is not configured for model prefix: {prefix.value}")

        return api_key


def _parse_model_prefix(model: str) -> AIProviderName:
    prefix = model.split("/", maxsplit=1)[0]
    try:
        return AIProviderName(prefix)
    except ValueError as exc:
        raise AIProviderMismatchError(f"AI model provider prefix is not supported: {prefix}") from exc
