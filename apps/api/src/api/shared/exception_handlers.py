from fastapi import Request
from fastapi.responses import JSONResponse

from api.shared.errors import AppError


async def app_error_handler(_request: Request, exception: Exception) -> JSONResponse:
    if not isinstance(exception, AppError):
        exception = AppError()  # Convert to 500 error

    return JSONResponse(
        status_code=exception.status_code,
        content={
            "error": {
                "code": exception.code,
                "message": exception.message,
            }
        },
    )
