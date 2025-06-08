from sqlalchemy import or_
from sqlalchemy.orm import Session
from src.models.employee_model import Employee
from typing import Optional, List

class EmployeeRepository:
    # @staticmethod
    # def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    #     return db.query(Employee).offset(skip).limit(limit).all()
    
    @staticmethod  
    def get_all(db: Session, page: int = 1, per_page: int = 10, search: str = None):
        query = db.query(Employee)
        
        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Employee.name.ilike(search_filter),
                    Employee.email.ilike(search_filter),
                    Employee.divisi.ilike(search_filter)
                )
            )
        
        # Get total count
        total_data = query.count()
        
        # Calculate pagination
        total_pages = (total_data + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Get paginated data
        employees = query.offset(offset).limit(per_page).all()
        
        return {
            "employees": employees,
            "meta": {
                "page": page,
                "perPage": per_page,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }
        
    @staticmethod
    def get_all_with_face_data(db: Session) -> List[Employee]:
        """Get all employees that have face encoding data"""
        return db.query(Employee).filter(Employee.face_encoding.isnot(None)).all()

    @staticmethod
    def get_by_id(db: Session, employee_id: int) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.email == email).first()

    @staticmethod
    def create(db: Session, name: str, email: str, date_of_birth, divisi: str, address: str, image_url: str = None, face_encoding: str = None) -> Employee:
        new_employee = Employee(
            name=name,
            email=email,
            date_of_birth=date_of_birth,
            divisi=divisi,
            address=address,
            image_url=image_url,
            face_encoding=face_encoding
        )
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        return new_employee

    @staticmethod
    def update(db: Session, employee_id: int, **kwargs) -> Optional[Employee]:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(employee, key, value)
            db.commit()
            db.refresh(employee)
        return employee

    @staticmethod
    def delete(db: Session, employee_id: int) -> bool:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            db.delete(employee)
            db.commit()
            return True
        return False