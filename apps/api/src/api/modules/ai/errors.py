from api.shared.errors import AppError, ValidationError


class AIProviderError(AppError):
    code = "ai_provider_error"
    message = "AI provider request failed"


class AIProviderMismatchError(AppError):
    status_code = 400
    code = "ai_provider_mismatch"
    message = "AI model does not match a configured provider"


class NoAvailableAIModelsError(AppError):
    status_code = 503
    code = "no_available_ai_models"
    message = "No AI models are available"


class UnsupportedEmbeddingModelError(ValidationError):
    code = "unsupported_embedding_model"
    message = "Selected embedding model is not available"


class UnsupportedLanguageModelError(ValidationError):
    code = "unsupported_language_model"
    message = "Selected language model is not available"
