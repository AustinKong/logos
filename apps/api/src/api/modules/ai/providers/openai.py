from api.modules.ai.models import AIEmbeddingModel, AILanguageModel, AIProviderName
from api.modules.ai.providers.litellm import LiteLLMProvider


class OpenAIProvider(LiteLLMProvider):
    def list_language_models(self) -> list[AILanguageModel]:
        return [
            AILanguageModel(
                id="openai/gpt-5-nano",
                label="GPT-5 Nano",
                provider=AIProviderName.OPENAI,
                supports_reasoning=True,
            ),
            AILanguageModel(
                id="openai/gpt-4o-mini",
                label="GPT-4o Mini",
                provider=AIProviderName.OPENAI,
                supports_reasoning=False,
            ),
            AILanguageModel(
                id="openai/gpt-4.1-mini",
                label="GPT-4.1 Mini",
                provider=AIProviderName.OPENAI,
                supports_reasoning=False,
            ),
        ]

    def list_embedding_models(self) -> list[AIEmbeddingModel]:
        return [
            AIEmbeddingModel(
                id="openai/text-embedding-3-small",
                label="Text Embedding 3 Small",
                provider=AIProviderName.OPENAI,
            )
        ]
