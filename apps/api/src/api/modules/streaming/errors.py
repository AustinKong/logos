from api.shared.errors import AppError, ConflictError, NotFoundError


class StreamNotFoundError(NotFoundError):
    message = "Stream not found"


class StreamAlreadyOpenError(AppError):
    message = "Stream is already open"


class StreamCursorExpiredError(ConflictError):
    message = "Stream cursor is no longer available"
