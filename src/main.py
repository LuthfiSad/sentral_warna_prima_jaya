import os
from fastapi import FastAPI
import uvicorn

from src.routes import auth_routes
from src.routes import face_routes
from src.utils.error import app_error_handler, AppError, validation_exception_handler
from src.config.settings import PORT
from fastapi.exceptions import RequestValidationError

app = FastAPI()

# Default route
@app.get("/")
def read_root():
    return {"message": "Welcome to the API!"}

# Include authentication routes
app.include_router(auth_routes.router, prefix="/auth")
app.include_router(face_routes.router, prefix="/faces")

# Custom error handler
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Run server on specified port
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=int(PORT), reload=True)
