from api.shared.errors import ConflictError, NotFoundError, ValidationError


class AskUserStartedEventNotFoundError(NotFoundError):
    message = "Ask-user request not found"


class AskUserAlreadyAnsweredError(ConflictError):
    message = "Ask-user request has already been answered"


class InvalidAskUserAnswerError(ValidationError):
    pass
