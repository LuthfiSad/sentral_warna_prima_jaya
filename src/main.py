# main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

from src.routes import attendance_routes, employee_routes, user_routes, report_routes
from src.utils.error import app_error_handler, AppError, validation_exception_handler
from src.config.settings import PORT
from fastapi.exceptions import RequestValidationError
from src.middlewares.jwt_auth_middleware import JWTAuthMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.utils.response import handle_response

app = FastAPI(title="Employee Management System", version="1.0.0")

# Default route
@app.get("/")
def read_root():
    return {"message": "Welcome to My Api!"}

app.add_middleware(JWTAuthMiddleware)

# Include routes
app.include_router(user_routes.router, prefix="/users", tags=["Authentication"])
app.include_router(employee_routes.router, prefix="/employees", tags=["Employees"])
app.include_router(attendance_routes.router, prefix="/attendances", tags=["Attendances"])
app.include_router(report_routes.router, prefix="/reports", tags=["Reports"])

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
        status_code=exc.status_code
    )

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        content=handle_response(
            status=exc.status_code,
            code="HTTP_ERROR",
            message=str(exc.detail)
        ),
        status_code=exc.status_code
    )

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=int(PORT), reload=True)