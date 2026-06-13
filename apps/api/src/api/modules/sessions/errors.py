from api.shared.errors import NotFoundError


class SessionNotFoundError(NotFoundError):
    message = "Session not found"
