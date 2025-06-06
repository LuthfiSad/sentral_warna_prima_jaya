from fastapi import Request
from jose import jwt, JWTError
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from src.config.settings import SECRET_KEY, ALGORITHM
from src.utils.message_code import MESSAGE_CODE
from src.utils.response import handle_response

def is_excluded_path(path: str) -> bool:
    EXCLUDED_PATHS = ["/auth/register", "/auth/login", "/"]
    return path in EXCLUDED_PATHS

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if is_excluded_path(request.url.path):
            return await call_next(request)
          
        authorization: str = request.headers.get("Authorization")
        
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content=handle_response(401, MESSAGE_CODE.UNAUTHORIZED, "Missing or invalid JWT token")
            )
        
        token = authorization.split("Bearer ")[1].strip()
        
        try:
            # payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            payload = jwt.get_unverified_claims(token)
            sub = payload.get("sub", {})  # Ambil sub, default ke dict kosong jika tidak ada
            user_id = sub.get("id")  # ✅ Ambil "id" dari dalam "sub"
            username = sub.get("name") 
            exp = payload.get("exp")
            
            # Cek apakah token sudah kedaluwarsa
            if exp is None or datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
                return JSONResponse(
                    status_code=401,
                    content=handle_response(401, MESSAGE_CODE.UNAUTHORIZED, "Token expired")
                )
            
            # Pastikan user_id ada di dalam token
            if user_id is None:
                return JSONResponse(
                    status_code=401,
                    content=handle_response(401, MESSAGE_CODE.UNAUTHORIZED, "Token missing user_id claim")
                )
            
            # Simpan user ke dalam request state agar bisa digunakan di route
            request.state.user = {
                "user_id": user_id,
                "username": username
            }
            user = getattr(request.state, "user", None)

        except JWTError:
            return JSONResponse(
                status_code=401,
                content=handle_response(401, MESSAGE_CODE.UNAUTHORIZED, "Invalid token")
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content=handle_response(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, str(e))
            )

        return await call_next(request)
