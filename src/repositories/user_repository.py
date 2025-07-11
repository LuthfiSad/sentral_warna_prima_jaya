from datetime import date
from pydantic import TypeAdapter
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from src.models.attendance_model import Attendance
from src.models.employee_model import Employee
from src.models.user_model import User
from typing import Optional

from src.schemas.user_schema import UserResponseSchema

class UserRepository:
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[UserResponseSchema]:
        user = db.query(User).options(joinedload(User.employee)).filter(User.username == username).first()
        return UserResponseSchema.model_validate(user) if user else None

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[UserResponseSchema]:
        user = db.query(User).options(joinedload(User.employee)).filter(User.email == email).first()
        return UserResponseSchema.model_validate(user) if user else None

    @staticmethod
    def get_by_login(db: Session, login: str) -> Optional[User]:
        """Get user by username or email"""
        user = db.query(User).options(joinedload(User.employee)).filter(
            (User.username == login) | (User.email == login)
        ).first()
        return user

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
    def get_all(db: Session, page: int = 1, perPage: int = 10, search: str = None):
        query = db.query(User).options(joinedload(User.employee))
        
        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            search_lower = search.lower()
            # query = query.outerjoin(Employee).filter(
            #     or_(
            #         User.username.ilike(search_filter),
            #         User.email.ilike(search_filter),
            #         User.is_admin.is_(search_filter == "admin"),
            #         Employee.name.ilike(search_filter)
            #     )
            # )
            
            filters = [
                User.username.ilike(search_filter),
                User.email.ilike(search_filter),
                Employee.name.ilike(search_filter)
            ]

            if search_lower == "admin":
                filters.append(User.is_admin.is_(True))
            elif search_lower in ["karyawan", "employee"]:
                filters.append(User.is_admin.is_(False))

            query = query.outerjoin(Employee).filter(or_(*filters))
        
        # Get total count
        total_data = query.count()
        
        # Calculate pagination
        total_pages = (total_data + perPage - 1) // perPage
        offset = (page - 1) * perPage
        
        # Get paginated data
        users = query.offset(offset).limit(perPage).all()
        
        users_schema = TypeAdapter(list[UserResponseSchema]).validate_python(users)
        
        return {
            "users": users_schema,
            "meta": {
                "page": page,
                "perPage": perPage,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        user = db.query(User).options(joinedload(User.employee)).filter(User.id == user_id).first()

        if user and user.employee:
            # Cari attendance hari ini untuk employee tersebut
            today = date.today()
            today_attendance = (
                db.query(Attendance)
                .filter(
                    Attendance.employee_id == user.employee.id,
                    Attendance.date == today
                )
                .first()
            )

            # Inject attendance ke dalam employee
            user.employee.attendance_today = today_attendance
        return UserResponseSchema.model_validate(user) if user else None
    
    def get_by_employee_id(self, db: Session, employee_id: int):
        return db.query(User).filter(User.karyawan_id == employee_id).first()
    
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