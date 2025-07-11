# src/repositories/attendance_repository.py
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, List
from src.models.attendance_model import Attendance
from src.models.employee_model import Employee
from sqlalchemy.orm import joinedload

class AttendanceRepository:
    @staticmethod
    def create_checkin(db: Session, employee_id: int, attendance_date: date, 
                      checkin_time: datetime, latitude: float, longitude: float, 
                      image_url: str) -> Attendance:
        new_attendance = Attendance(
            employee_id=employee_id,
            date=attendance_date,
            checkin_time=checkin_time,
            checkin_latitude=latitude,
            checkin_longitude=longitude,
            checkin_image_url=image_url
        )
        db.add(new_attendance)
        db.commit()
        db.refresh(new_attendance)
        return new_attendance

    @staticmethod
    def update_checkin(db: Session, attendance_id: int, checkin_time: datetime,
                      latitude: float, longitude: float, image_url: str) -> Optional[Attendance]:
        attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if attendance:
            attendance.checkin_time = checkin_time
            attendance.checkin_latitude = latitude
            attendance.checkin_longitude = longitude
            attendance.checkin_image_url = image_url
            db.commit()
            db.refresh(attendance)
        return attendance

    @staticmethod
    def update_checkout(db: Session, attendance_id: int, checkout_time: datetime,
                       latitude: float, longitude: float, image_url: str) -> Optional[Attendance]:
        attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
        if attendance:
            attendance.checkout_time = checkout_time
            attendance.checkout_latitude = latitude
            attendance.checkout_longitude = longitude
            attendance.checkout_image_url = image_url
            db.commit()
            db.refresh(attendance)
        return attendance

    # @staticmethod
    # def get_by_id(db: Session, attendance_id: int) -> Optional[Attendance]:
    #     return db.query(Attendance).filter(Attendance.id == attendance_id).first()

    @staticmethod
    def get_by_employee_and_date(db: Session, employee_id: int, attendance_date: date) -> Optional[Attendance]:
        return db.query(Attendance).filter(
            and_(Attendance.employee_id == employee_id, Attendance.date == attendance_date)
        ).first()
        
    @staticmethod
    def get_all(db: Session, page: int = 1, perPage: int = 10, search: str = None, employee_id: int = None):
        query = db.query(Attendance).options(joinedload(Attendance.employee)).join(Employee)
        
        # Apply employee filter if provided (for non-admin users)
        if employee_id:
            query = query.filter(Attendance.employee_id == employee_id)
        
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
        attendances = query.offset(offset).limit(perPage).all()
        
        return {
            "attendances": attendances,
            "meta": {
                "page": page,
                "perPage": perPage,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }

    @staticmethod
    def get_by_id(db: Session, attendance_id: int, employee_id: int = None) -> Optional[Attendance]:
        query = db.query(Attendance).options(joinedload(Attendance.employee)).join(Employee).filter(Attendance.id == attendance_id)
        
        # Add employee filter if provided (for non-admin users)
        if employee_id:
            query = query.filter(Attendance.employee_id == employee_id)
        
        return query.first()

    @staticmethod
    def get_by_ids(db: Session, attendance_ids: List[int]) -> List[Attendance]:
        return db.query(Attendance).filter(Attendance.id.in_(attendance_ids)).all()

    @staticmethod
    def delete_multiple(db: Session, attendance_ids: List[int]) -> int:
        deleted_count = db.query(Attendance).filter(Attendance.id.in_(attendance_ids)).delete(synchronize_session=False)
        db.commit()
        return deleted_count

    # @staticmethod
    # def get_all(db: Session, page: int = 1, perPage: int = 10, search: str = None):
    #     query = db.query(Attendance).join(Employee)
        
    #     # Apply search filter (searching in employee data)
    #     if search:
    #         search_filter = f"%{search}%"
    #         query = query.filter(
    #             or_(
    #                 Employee.name.ilike(search_filter),
    #                 Employee.email.ilike(search_filter),
    #                 Employee.divisi.ilike(search_filter)
    #             )
    #         )
        
    #     # Get total count
    #     total_data = query.count()
        
    #     # Calculate pagination
    #     total_pages = (total_data + perPage - 1) // perPage
    #     offset = (page - 1) * perPage
        
    #     # Get paginated data with employee relationship
    #     attendances = query.offset(offset).limit(perPage).all()
        
    #     return {
    #         "attendances": attendances,
    #         "meta": {
    #             "page": page,
    #             "perPage": perPage,
    #             "totalPages": total_pages,
    #             "totalData": total_data
    #         }
    #     }
    
    # @staticmethod
    # def get_all(db: Session, page: int = 1, perPage: int = 10, 
    #            employee_id: Optional[int] = None, start_date: Optional[date] = None,
    #            end_date: Optional[date] = None):
    #     query = db.query(Attendance)
        
    #     # Apply filters
    #     if employee_id:
    #         query = query.filter(Attendance.employee_id == employee_id)
        
    #     if start_date:
    #         query = query.filter(Attendance.date >= start_date)
            
    #     if end_date:
    #         query = query.filter(Attendance.date <= end_date)
        
    #     # Get total count
    #     total_data = query.count()
        
    #     # Calculate pagination
    #     total_pages = (total_data + perPage - 1) // perPage
    #     offset = (page - 1) * perPage
        
    #     # Get paginated data with employee relationship
    #     attendances = query.offset(offset).limit(perPage).all()
        
    #     return {
    #         "attendances": attendances,
    #         "meta": {
    #             "page": page,
    #             "perPage": perPage,
    #             "totalPages": total_pages,
    #             "totalData": total_data
    #         }
    #     }