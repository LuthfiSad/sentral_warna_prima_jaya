# ==================== ADDITIONAL SCHEMAS ====================

# Tambahkan ke src/schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Tambahkan ke src/schemas/employee_schema.py  



# ==================== UPDATED REPOSITORIES ====================

# Update src/repositories/employee_repository.py - tambahkan method ini
from sqlalchemy import func, or_

from src.routes import user_routes

class EmployeeRepository:
    # ... existing methods ...
    
    

# Update src/repositories/user_repository.py - tambahkan method ini
class UserRepository:
    # ... existing methods ...
    
    


# ==================== UPDATED SERVICES ====================

# Update src/services/employee_service.py - replace get_all_employees method
class EmployeeService:
    
    
    # ... existing methods remain the same ...

# Tambahkan src/services/user_service.py
from sqlalchemy.orm import Session
from src.repositories.user_repository import UserRepository
from src.repositories.employee_repository import EmployeeRepository
from src.libs.security import hash_password
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE

class UserService:
    


# ==================== UPDATED CONTROLLERS ====================

# Update src/controllers/employee_controller.py - replace get_all_employees method
class EmployeeController:
    
    
    # ... existing methods remain the same ...

# Tambahkan src/controllers/user_controller.py
from fastapi import Depends
from sqlalchemy.orm import Session
from src.schemas.user_schema import UserUpdateSchema, UserResetPasswordSchema
from src.services.user_service import UserService
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.config.database import get_db

class UserController:
    


# ==================== UPDATED ROUTES ====================

# Update src/routes/employee_routes.py - replace get_all_employees route


# Tambahkan src/routes/user_routes.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.controllers.user_controller import UserController
from src.middlewares.catch_wrapper import catch_exceptions
from src.middlewares.admin_middleware import require_admin
from src.config.database import get_db
from src.schemas.user_schema import UserUpdateSchema, UserResetPasswordSchema

router = APIRouter()




# ==================== UPDATE MAIN.PY ====================

# Tambahkan import di main.py
from src.routes import employee_routes, user_routes

# Tambahkan route di main.py
app.include_router(user_routes.router, prefix="/users", tags=["Users"])


# ==================== USAGE EXAMPLES ====================

"""
API Endpoints dengan Pagination dan Search:

1. GET /employees/?page=1&per_page=10&search=john
   Response:
   {
     "status": 200,
     "code": "SUCCESS",
     "message": "Employees retrieved successfully",
     "data": [...employees...],
     "meta": {
       "page": 1,
       "perPage": 10,
       "totalPages": 5,
       "totalData": 45
     }
   }

2. GET /users/?page=2&per_page=5&search=admin
   Response: Similar structure with users data

3. PUT /users/1
   Body: {
     "username": "new_username",
     "email": "new@email.com", 
     "is_admin": true
   }

4. POST /users/1/reset-password
   Body: {
     "password": "newpassword123",
     "confirm_password": "newpassword123"
   }

5. DELETE /users/1
   Response: Success message
"""