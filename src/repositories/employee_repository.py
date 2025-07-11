from datetime import date
from sqlalchemy import or_
from sqlalchemy.orm import Session
from src.models.attendance_model import Attendance
from src.models.employee_model import Employee
from typing import Optional, List

class EmployeeRepository:
    # @staticmethod
    # def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    #     return db.query(Employee).offset(skip).limit(limit).all()
    
    @staticmethod  
    def get_all(db: Session, page: int = 1, perPage: int = 10, search: str = None):
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
        total_pages = (total_data + perPage - 1) // perPage
        offset = (page - 1) * perPage
        
        # Get paginated data
        employees = query.offset(offset).limit(perPage).all()
        
        return {
            "employees": employees,
            "meta": {
                "page": page,
                "perPage": perPage,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }
        
    @staticmethod
    def get_all_with_face_data(db: Session) -> List[Employee]:
        """Get all employees that have face encoding data, with today's attendance"""
        employees = db.query(Employee).filter(Employee.face_encoding.isnot(None)).all()
        today = date.today()

        # Inject attendance_today untuk masing-masing employee
        for emp in employees:
            attendance = (
                db.query(Attendance)
                .filter(
                    Attendance.employee_id == emp.id,
                    Attendance.date == today
                )
                .first()
            )
            emp.attendance_today = attendance

        return employees


    @staticmethod
    def get_by_id(db: Session, employee_id: int) -> Optional[Employee]:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        today = date.today()
        today_attendance = (
            db.query(Attendance)
            .filter(
                Attendance.employee_id == employee.id,
                Attendance.date == today
            )
            .first()
        )
        employee.attendance_today = today_attendance
        return employee

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.email == email).first()

    @staticmethod
    def get_all_active(db: Session):
        return db.query(Employee).filter(Employee.is_active == True).all()

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