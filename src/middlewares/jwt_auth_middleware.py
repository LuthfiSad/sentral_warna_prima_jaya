import json
from typing import Any, Dict, Optional
from fastapi import Request
from jose import jwt, JWTError
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from src.utils.message_code import MESSAGE_CODE
from src.utils.response import handle_response

def is_excluded_path(path: str) -> bool:
    EXCLUDED_PATHS = [
        "/users/auth/register", 
        "/users/auth/login", 
        "/",
    ]
    return path in EXCLUDED_PATHS

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # ✅ Handle preflight requests (OPTIONS)
        if request.method == "OPTIONS":
            return await call_next(request)
            
        if is_excluded_path(request.url.path):
            return await call_next(request)
          
        authorization: str = request.headers.get("Authorization")
        
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content=handle_response(401, MESSAGE_CODE.UNAUTHORIZED, "Missing or invalid JWT token"),
                headers={
                    "Access-Control-Allow-Origin": "*",  # ✅ Tambahkan CORS header
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type",
                }
            )
        
        token = authorization.split("Bearer ")[1].strip()
        
        try:
            # payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            payload = jwt.get_unverified_claims(token)
            sub = payload.get("sub", {})  # Ambil sub, default ke dict kosong jika tidak ada
            user_id = sub.get("id")  # ✅ Ambil "id" dari dalam "sub"
            username = sub.get("username") 
            is_admin = sub.get("is_admin")
            karyawan_id = sub.get("karyawan_id")
            exp = payload.get("exp")
            
            # Cek apakah token sudah kedaluwarsa
            if exp is None or datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
                return JSONResponse(
                    status_code=401,
                    content=handle_response(401, MESSAGE_CODE.UNAUTHORIZED, "Token expired"),
                    headers={
                        "Access-Control-Allow-Origin": "*",  # ✅ Tambahkan CORS header
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "Authorization, Content-Type",
                    }
                )
            
            # Pastikan user_id ada di dalam token
            if user_id is None:
                return JSONResponse(
                    status_code=401,
                    content=handle_response(401, MESSAGE_CODE.UNAUTHORIZED, "Token missing user_id claim"),
                    headers={
                        "Access-Control-Allow-Origin": "*",  # ✅ Tambahkan CORS header
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                        "Access-Control-Allow-Headers": "Authorization, Content-Type",
                    }
                )
            
            # Simpan user ke dalam request state agar bisa digunakan di route
            request.state.user = {
                "user_id": user_id,
                "username": username,
                "is_admin": is_admin,
                "karyawan_id": karyawan_id
            }

        except JWTError:
            return JSONResponse(
                status_code=401,
                content=handle_response(401, MESSAGE_CODE.UNAUTHORIZED, "Invalid token"),
                headers={
                    "Access-Control-Allow-Origin": "*",  # ✅ Tambahkan CORS header
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type",
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content=handle_response(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, str(e)),
                headers={
                    "Access-Control-Allow-Origin": "*",  # ✅ Tambahkan CORS header
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Authorization, Content-Type",
                }
            )

        return await call_next(request)

async def get_current_user_or_none(request: Request) -> Optional[Dict[str, Any]]:
    """Returns current user dict if authenticated, None otherwise"""
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split("Bearer ")[1].strip()
    if not token:
        return None
    
    try:
        payload = jwt.get_unverified_claims(token)
        sub = payload.get("sub", {})
        
        # Check token expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, timezone.utc) < datetime.now(timezone.utc):
            return None
        
        print(sub.get("karyawan_id"), "get_current_user_or_none")
        return {
            "user_id": sub.get("id"),
            "username": sub.get("username"),
            "is_admin": sub.get("is_admin", False),
            "karyawan_id": sub.get("karyawan_id", None)
        }
    except (JWTError, AttributeError):
        return None