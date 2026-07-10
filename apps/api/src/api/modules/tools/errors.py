from api.shared.errors import ValidationError


class UnknownToolError(ValidationError):
    pass


class InvalidToolArgumentsError(ValidationError):
    pass
