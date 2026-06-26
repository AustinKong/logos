from api.shared.errors import AppError


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
