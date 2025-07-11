# src/services/attendance_service.py
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional
from src.services.employee_service import EmployeeService
from src.services.location_service import LocationService
from src.repositories.attendance_repository import AttendanceRepository
from src.libs.supabase import upload_image_to_supabase
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE

class AttendanceService:
    @staticmethod
    async def checkin(db: Session, image_data: bytes, latitude: float, longitude: float, employee_id: Optional[int]):
        """
        Process check-in with face verification and location validation
        """
        try:
            # 1. Verify face
            face_result = EmployeeService.verify_face(db, image_data, employee_id)
            employee_id = face_result["id"]
            
            # 2. Validate location
            location_result = LocationService.validate_location(latitude, longitude)
            
            # 3. Check if already checked in today
            today = date.today()
            existing_attendance = AttendanceRepository.get_by_employee_and_date(db, employee_id, today)
            
            if existing_attendance and existing_attendance.checkin_time:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Already checked in today")
            
            # 4. Upload image to storage
            image_url = await upload_image_to_supabase(image_data)
            if isinstance(image_url, AppError):
                raise image_url
            
            # 5. Create or update attendance record
            if existing_attendance:
                # Update existing record
                attendance = AttendanceRepository.update_checkin(
                    db, existing_attendance.id, datetime.now(), 
                    latitude, longitude, image_url
                )
            else:
                # Create new record
                attendance = AttendanceRepository.create_checkin(
                    db, employee_id, today, datetime.now(),
                    latitude, longitude, image_url
                )
            
            return {
                "attendance_id": attendance.id,
                "employee": {
                    "id": face_result["id"],
                    "name": face_result["name"],
                    "email": face_result["email"],
                    "divisi": face_result["divisi"]
                },
                "checkin_time": attendance.checkin_time.isoformat(),
                "location": location_result,
                "message": "Check-in successful"
            }
            
        except AppError:
            raise

    @staticmethod
    async def checkout(db: Session, image_data: bytes, latitude: float, longitude: float, employee_id: Optional[int]):
        """
        Process check-out with face verification and location validation
        """
        try:
            # 1. Verify face
            face_result = EmployeeService.verify_face(db, image_data, employee_id)
            employee_id = face_result["id"]
            
            # 2. Validate location
            location_result = LocationService.validate_location(latitude, longitude)
            
            # 3. Check if already checked in today
            today = date.today()
            attendance = AttendanceRepository.get_by_employee_and_date(db, employee_id, today)
            
            if not attendance or not attendance.checkin_time:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Must check-in first before check-out")
            
            if attendance.checkout_time:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Already checked out today")
            
            # 4. Upload image to storage
            image_url = await upload_image_to_supabase(image_data)
            if isinstance(image_url, AppError):
                raise image_url
            
            # 5. Update attendance record with checkout
            updated_attendance = AttendanceRepository.update_checkout(
                db, attendance.id, datetime.now(),
                latitude, longitude, image_url
            )
            
            # Calculate work duration
            work_duration = updated_attendance.checkout_time - updated_attendance.checkin_time
            
            return {
                "attendance_id": updated_attendance.id,
                "employee": {
                    "id": face_result["id"],
                    "name": face_result["name"],
                    "email": face_result["email"],
                    "divisi": face_result["divisi"]
                },
                "checkin_time": updated_attendance.checkin_time.isoformat(),
                "checkout_time": updated_attendance.checkout_time.isoformat(),
                "work_duration": str(work_duration),
                "location": location_result,
                "message": "Check-out successful"
            }
            
        except AppError:
            raise

    # @staticmethod
    # def get_all_attendance(db: Session, page: int = 1, perPage: int = 10, 
    #                       employee_id: Optional[int] = None,
    #                       start_date: Optional[date] = None,
    #                       end_date: Optional[date] = None):
    #     """
    #     Get paginated attendance records with filters
    #     """
    #     return AttendanceRepository.get_all(db, page, perPage, employee_id, start_date, end_date)
    
    @staticmethod
    def get_all_attendance(db: Session, page: int = 1, perPage: int = 10, search: str = None, employee_id: Optional[int] = None):
        return AttendanceRepository.get_all(db, page, perPage, search, employee_id)

    @staticmethod
    def get_attendance_by_id(db: Session, attendance_id: int, employee_id: int = None):
        """
        Get attendance by ID
        """
        attendance = AttendanceRepository.get_by_id(db, attendance_id, employee_id)
        if not attendance:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Attendance record not found")
        return attendance