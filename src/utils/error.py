from fastapi.responses import JSONResponse
from fastapi import Request
from src.utils.response import handle_response
from fastapi.exceptions import RequestValidationError


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        # Ambil field terakhir dari loc (biasanya nama field)
        field = error['loc'][-1] if error['loc'] else "unknown"
        errors[field] = error["msg"]

    return JSONResponse(
        content=handle_response(
            status=400,
            code="VALIDATION_ERROR",
            message="Validation failed",
            error=errors,
        ),
        status_code=400,
    )

async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        content=handle_response(exc.status_code, exc.code, exc.message),
        status_code=exc.status_code,
    )