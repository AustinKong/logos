from api.modules.ai.models import AIModel, AIProviderName

AI_MODEL_CATALOG = [
    AIModel(id="openai/gpt-5-nano", label="GPT-5 Nano", provider=AIProviderName.OPENAI, supports_reasoning=True),
    AIModel(id="openai/gpt-4o-mini", label="GPT-4o Mini", provider=AIProviderName.OPENAI, supports_reasoning=False),
    AIModel(id="openai/gpt-4.1-mini", label="GPT-4.1 Mini", provider=AIProviderName.OPENAI, supports_reasoning=False),
    AIModel(
        id="anthropic/claude-3-5-haiku",
        label="Claude 3.5 Haiku",
        provider=AIProviderName.ANTHROPIC,
        supports_reasoning=False,
    ),
]
