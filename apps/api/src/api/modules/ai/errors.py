from api.shared.errors import AppError


class AIProviderError(AppError):
    code = "ai_provider_error"
    message = "AI provider request failed"


class AIProviderMismatchError(AppError):
    status_code = 400
    code = "ai_provider_mismatch"
    message = "AI model does not match a configured provider"
