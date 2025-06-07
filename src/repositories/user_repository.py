from pydantic import TypeAdapter
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from src.models.employee_model import Employee
from src.models.user_model import User
from typing import Optional

from src.schemas.user_schema import UserResponseSchema

class UserRepository:
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).options(joinedload(User.employee)).filter(User.username == username).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).options(joinedload(User.employee)).filter(User.email == email).first()

    @staticmethod
    def get_by_login(db: Session, login: str) -> Optional[User]:
        """Get user by username or email"""
        return db.query(User).options(joinedload(User.employee)).filter(
            (User.username == login) | (User.email == login)
        ).first()

    @staticmethod
    def create(db: Session, username: str, email: str, password_hash: str, karyawan_id: int, is_admin: bool = False) -> User:
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            karyawan_id=karyawan_id,
            is_admin=is_admin
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    @staticmethod
    def get_all(db: Session, page: int = 1, per_page: int = 10, search: str = None):
        query = db.query(User).options(joinedload(User.employee))
        
        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.outerjoin(Employee).filter(
                or_(
                    User.username.ilike(search_filter),
                    User.email.ilike(search_filter),
                    Employee.name.ilike(search_filter)
                )
            )
        
        # Get total count
        total_data = query.count()
        
        # Calculate pagination
        total_pages = (total_data + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Get paginated data
        users = query.offset(offset).limit(per_page).all()
        
        users_schema = TypeAdapter(list[UserResponseSchema]).validate_python(users)
        
        return {
            "users": users_schema,
            "meta": {
                "page": page,
                "perPage": per_page,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        user = db.query(User).options(joinedload(User.employee)).filter(User.id == user_id).first()
        return UserResponseSchema.model_validate(user)
    
    @staticmethod
    def update(db: Session, user_id: int, **kwargs) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(user, key, value)
            db.commit()
            db.refresh(user)
        return user
    
    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False