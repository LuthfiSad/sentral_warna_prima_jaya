from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE

def is_excluded_path(path: str) -> bool:
    EXCLUDED_PATHS = ["/users/auth/register", "/users/auth/login"]
    return path in EXCLUDED_PATHS

class CheckLuthfiMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if is_excluded_path(request.url.path):
            return await call_next(request)
          
        user = getattr(request.state, "user", None)
        if not user or user.get("username") != "luthfi":
          return JSONResponse(
                status_code=403,
                content=handle_response(403, MESSAGE_CODE.FORBIDDEN, "Access restricted to user 'luthfi' only")
            )
        return await call_next(request)


async def check_luthfi_user(request: Request):
    user = getattr(request.state, "user", None)
    if not user or user.get("username") != "luthfi":
        return JSONResponse(
            status_code=403,
            content=handle_response(403, MESSAGE_CODE.FORBIDDEN, "Access restricted to user 'luthfi' only")
        )
    return user