from sqlalchemy.orm import Session
from src.config.settings import ADMIN_KEY
from src.models.user_model import User
from src.repositories.user_repository import UserRepository
from src.repositories.employee_repository import EmployeeRepository
from src.libs.security import hash_password, verify_password
from src.libs.jwt import create_access_token
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE

class UserService:
    @staticmethod
    def register_user(db: Session, username: str, email: str, password: str, is_admin: bool = False, key_admin: str = None):
        # Check if username already exists
        if UserRepository.get_by_username(db, username):
            raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Username already exists")

        # Check if email already exists in users table
        if UserRepository.get_by_email(db, email):
            raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Email already registered as user")

        # Check if employee with this email exists
        if is_admin:
            if not key_admin or key_admin != ADMIN_KEY:
                raise AppError(403, MESSAGE_CODE.FORBIDDEN, "Invalid admin key")
        
        # Jika bukan admin, lakukan pengecekan employee
        employee = None
        if not is_admin:
            employee = EmployeeRepository.get_by_email(db, email)
            if not employee:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, 
                            "Email not found in employee database. Please contact admin.")
            
            # Cek apakah employee sudah punya akun
            existing_user = db.query(User).filter(User.karyawan_id == employee.id).first()
            if existing_user:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, 
                            "Employee already has a user account")

        hashed_password = hash_password(password)
        user = UserRepository.create(db, username, email, hashed_password, employee.id, is_admin)
        return user

    @staticmethod
    def authenticate_user(db: Session, login: str, password: str):
        user = UserRepository.get_by_login(db, login)
        if not user or not verify_password(password, user.password_hash):
            raise AppError(401, MESSAGE_CODE.UNAUTHORIZED, "Invalid credentials")

        token_data = {
            "sub": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin,
                "karyawan_id": user.karyawan_id
            }
        }
        token = create_access_token(token_data)
        return {"access_token": token, "user": user}
    
    @staticmethod
    def get_all_users(db: Session, page: int = 1, per_page: int = 10, search: str = None):
        return UserRepository.get_all(db, page, per_page, search)
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "User not found")
        return user
    
    @staticmethod
    def update_user(db: Session, user_id: int, username: str = None, email: str = None, is_admin: bool = None, key_admin: str = None):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "User not found")
        
        # Check if username already exists (but not for current user)
        if username and username != user.username:
            existing_user = UserRepository.get_by_username(db, username)
            if existing_user:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Username already exists")
        
        # Check if email already exists (but not for current user)
        if email and email != user.email:
            existing_user = UserRepository.get_by_email(db, email)
            if existing_user:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Email already exists")
            
            # Also check if new email exists in employee database
            employee = EmployeeRepository.get_by_email(db, email)
            if not employee:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Email not found in employee database")
            
            # Update employee relationship if email changed
            if employee.id != user.karyawan_id:
                # Check if new employee already has a user
                existing_user_for_employee = db.query(User).filter(User.karyawan_id == employee.id).first()
                if existing_user_for_employee:
                    raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Employee already has a user account")
                
                # Update karyawan_id to new employee
                user = UserRepository.update(db, user_id, username=username, email=email, is_admin=is_admin, karyawan_id=employee.id)
            else:
                user = UserRepository.update(db, user_id, username=username, email=email, is_admin=is_admin)
        else:
            user = UserRepository.update(db, user_id, username=username, email=email, is_admin=is_admin)
        
        return user
    
    @staticmethod
    def reset_password(db: Session, user_id: int, new_password: str):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "User not found")
        
        hashed_password = hash_password(new_password)
        user = UserRepository.update(db, user_id, password_hash=hashed_password)
        return {"message": "Password reset successfully"}
    
    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "User not found")
        
        success = UserRepository.delete(db, user_id)
        if not success:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, "Failed to delete user")
        return {"message": "User deleted successfully"}