from fastapi import Response
from typing import Any, Dict, Optional

from typing import Any, Dict, Optional

def handle_response(
    status: int,
    code: str,
    message: str,
    data: Optional[Any] = None,
    meta: Optional[Dict[str, Any]] = None,
    error: Optional[Any] = None
):
    response = {
        "status": status,
        "code": code,
        "message": message,
        "data": data,
        "meta": meta,
        "error": error
    }

    return {key: value for key, value in response.items() if value is not None}
