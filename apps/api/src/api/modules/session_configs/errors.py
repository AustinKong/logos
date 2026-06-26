from api.shared.errors import NotFoundError, ValidationError


class SessionConfigNotFoundError(NotFoundError):
    code = "session_config_not_found"
    message = "Session config not found"


class UnsupportedParticipantCreateError(ValidationError):
    code = "unsupported_participant_create"
    message = "Participant type is not supported for session config creation"
