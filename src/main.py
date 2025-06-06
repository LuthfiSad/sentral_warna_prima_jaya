from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import uvicorn

from src.routes import auth_routes
from src.routes import face_routes
from src.utils.error import app_error_handler, AppError, validation_exception_handler
from src.config.settings import PORT
from fastapi.exceptions import RequestValidationError
from src.middlewares.jwt_auth_middleware import JWTAuthMiddleware
from src.middlewares.jwt_auth_username_middleware import CheckLuthfiMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.utils.response import handle_response

app = FastAPI()

# Default route
@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}

# @app.get("/test-error")
# async def test_error():
#     raise HTTPException(status_code=405, detail="Method Not Allowed")

# app.add_middleware(CheckLuthfiMiddleware)
app.add_middleware(JWTAuthMiddleware)

# @app.post("/restricted")
# async def restricted_route():
#     return {"message": "You have access because your username is 'luthfi'"}

# Include authentication routes
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(face_routes.router, prefix="/faces")

# Custom error handler
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
    if exc.status_code == 405:
        return JSONResponse(
            content=handle_response(
                status=405,
                code="HTTP_ERROR",
                message=str(exc.detail)
            ),
            status_code=405
        )
    # Untuk error Starlette lainnya
    return JSONResponse(
        content=handle_response(
            status=exc.status_code,
            code="HTTP_ERROR",
            message=str(exc.detail)
        ),
        status_code=exc.status_code
    )

# Run server on specified port
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=int(PORT), reload=True)
