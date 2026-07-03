from api.shared.errors import NotFoundError, ValidationError


class SessionConfigNotFoundError(NotFoundError):
    code = "session_config_not_found"
    message = "Session config not found"


class UnsupportedParticipantCreateError(ValidationError):
    code = "unsupported_participant_create"
    message = "Participant type is not supported for session config creation"


class UnsupportedParticipantModelError(ValidationError):
    code = "unsupported_participant_model"
    message = "Selected participant model is not available"


class UnsupportedReasoningModelError(ValidationError):
    code = "unsupported_reasoning_model"
    message = "Selected model does not support reasoning"
