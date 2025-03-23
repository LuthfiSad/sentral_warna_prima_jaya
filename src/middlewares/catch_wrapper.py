from fastapi import HTTPException
from functools import wraps
import asyncio
from src.utils.error import  AppError

def catch_exceptions(handler):
    @wraps(handler)
    async def async_wrapper(*args, **kwargs):
        try:
            return await handler(*args, **kwargs)
        except HTTPException as http_exc:
            raise http_exc
        except AppError as app_exc:  # Tangani AppError
            raise app_exc
        except Exception as exc:
            raise AppError(status_code=500, code="INTERNAL_SERVER_ERROR", message=str(exc))

    @wraps(handler)
    def sync_wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except HTTPException as http_exc:
            raise http_exc
        except AppError as app_exc:
            raise app_exc
        except Exception as exc:
            raise AppError(status_code=500, code="INTERNAL_SERVER_ERROR", message=str(exc))

    return async_wrapper if asyncio.iscoroutinefunction(handler) else sync_wrapper
