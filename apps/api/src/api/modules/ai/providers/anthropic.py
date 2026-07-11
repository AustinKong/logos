from api.modules.ai.models import AILanguageModel, AIProviderName
from api.modules.ai.providers.litellm import LiteLLMProvider


class AnthropicProvider(LiteLLMProvider):
    def list_language_models(self) -> list[AILanguageModel]:
        return [
            AILanguageModel(
                id="anthropic/claude-3-5-haiku",
                label="Claude 3.5 Haiku",
                provider=AIProviderName.ANTHROPIC,
                supports_reasoning=False,
            )
        ]
