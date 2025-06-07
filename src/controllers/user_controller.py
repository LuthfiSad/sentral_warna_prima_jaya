from fastapi import Depends
from sqlalchemy.orm import Session
from src.schemas.user_schema import UserRegisterSchema, UserLoginSchema, UserResetPasswordSchema, UserUpdateSchema
from src.services.user_service import UserService
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.config.database import get_db

class UserController:
    @staticmethod
    def register(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
        user = UserService.register_user(db, user_data.username, user_data.email, user_data.password, user_data.is_admin, user_data.key_admin)
        return handle_response(201, MESSAGE_CODE.CREATED, "User registered successfully", {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        })

    @staticmethod
    def login(user_data: UserLoginSchema, db: Session = Depends(get_db)):
        result = UserService.authenticate_user(db, user_data.login, user_data.password)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Login successful", {
            "access_token": result["access_token"],
            "user": {
                "id": result["user"].id,
                "username": result["user"].username,
                "email": result["user"].email,
                "is_admin": result["user"].is_admin,
                "employee": result["user"].employee
            }
        })
        
    @staticmethod
    async def get_all_users(
        page: int = 1,
        per_page: int = 10,
        search: str = None,
        db: Session = Depends(get_db)
    ):
        result = UserService.get_all_users(db, page, per_page, search)
        return handle_response(
            200,
            MESSAGE_CODE.SUCCESS,
            "Users retrieved successfully",
            result["users"],
            meta=result["meta"]
        )
    
    @staticmethod
    async def get_user(user_id: int, db: Session = Depends(get_db)):
        user = UserService.get_user_by_id(db, user_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "User retrieved successfully", user)
    
    @staticmethod
    async def update_user(user_id: int, user_data: UserUpdateSchema, db: Session = Depends(get_db)):
        user = UserService.update_user(
            db, user_id, user_data.username, user_data.email, user_data.is_admin, user_data.key_admin
        )
        return handle_response(200, MESSAGE_CODE.SUCCESS, "User updated successfully", user)
    
    @staticmethod
    async def reset_password(user_id: int, password_data: UserResetPasswordSchema, db: Session = Depends(get_db)):
        # Validate passwords match
        password_data.validate_passwords_match()
        
        result = UserService.reset_password(db, user_id, password_data.password)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Password reset successfully", result)
    
    @staticmethod
    async def delete_user(user_id: int, db: Session = Depends(get_db)):
        result = UserService.delete_user(db, user_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "User deleted successfully", result)