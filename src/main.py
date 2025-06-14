# main.py
import os
from fastapi import APIRouter, FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

from src.routes import attendance_routes, employee_routes, user_routes, report_routes
from src.utils.error import app_error_handler, AppError, validation_exception_handler
from src.config.settings import PORT
from fastapi.exceptions import RequestValidationError
from src.middlewares.jwt_auth_middleware import JWTAuthMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.utils.response import handle_response

# Import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Employee Management System", version="1.0.0")

# Default route
@app.get("/")
def read_root():
    return {"message": "Welcome to My Api!"}

# --- Konfigurasi CORS di sini ---
# ✅ Update origins to be more permissive and include both HTTP and potential HTTPS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://192.168.0.103"
    # Untuk production, ganti dengan domain yang sebenarnya
    # "https://yourdomain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # ✅ Atau gunakan ["*"] untuk development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],  # ✅ Tambahkan lebih banyak methods
    allow_headers=["*"],  # ✅ Allow all headers
    expose_headers=["*"],
    max_age=600  # Cache preflight response for 10 minutes
)
# --- Akhir Konfigurasi CORS ---

# ✅ Pastikan JWTAuthMiddleware berada setelah CORSMiddleware
app.add_middleware(JWTAuthMiddleware) 

# # Include routes
# app.include_router(user_routes.router, prefix="/users", tags=["Authentication"])
# app.include_router(employee_routes.router, prefix="/employees", tags=["Employees"])
# app.include_router(attendance_routes.router, prefix="/attendances", tags=["Attendances"])
# app.include_router(report_routes.router, prefix="/reports", tags=["Reports"])

api_router = APIRouter(prefix="/api")

# Tambahkan semua router ke api_router
api_router.include_router(user_routes.router, prefix="/users", tags=["Authentication"])
api_router.include_router(employee_routes.router, prefix="/employees", tags=["Employees"])
api_router.include_router(attendance_routes.router, prefix="/attendances", tags=["Attendances"])
api_router.include_router(report_routes.router, prefix="/reports", tags=["Reports"])

# Masukkan api_router ke aplikasi FastAPI
app.include_router(api_router)

# Custom error handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        content=handle_response(
            status=exc.status_code,
            code="HTTP_ERROR",
            message=str(exc.detail)
        ),
        status_code=exc.status_code,
        headers={  # ✅ Tambahkan CORS headers
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
        }
    )

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        content=handle_response(
            status=exc.status_code,
            code="HTTP_ERROR",
            message=str(exc.detail)
        ),
        status_code=exc.status_code,
        headers={  # ✅ Tambahkan CORS headers
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(PORT), reload=True)