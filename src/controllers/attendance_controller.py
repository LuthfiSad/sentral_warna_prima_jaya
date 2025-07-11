# src/controllers/attendance_controller.py
from fastapi import Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from src.services.attendance_service import AttendanceService
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.config.database import get_db

class AttendanceController:
    @staticmethod
    async def checkin(
        image: UploadFile = File(...),
        latitude: float = Form(...),
        longitude: float = Form(...),
        employee_id: Optional[int] = Form(None),
        db: Session = Depends(get_db)
    ):
        image_data = await image.read()
        result = await AttendanceService.checkin(db, image_data, latitude, longitude, employee_id)
        return handle_response(201, MESSAGE_CODE.CREATED, "Check-in successful", result)

    @staticmethod
    async def checkout(
        image: UploadFile = File(...),
        latitude: float = Form(...),
        longitude: float = Form(...),
        employee_id: Optional[int] = Form(None),
        db: Session = Depends(get_db)
    ):
        image_data = await image.read()
        result = await AttendanceService.checkout(db, image_data, latitude, longitude, employee_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Check-out successful", result)

    @staticmethod
    async def get_all_attendance(
        page: int = 1,
        perPage: int = 10,
        search: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: dict = None  # Add this parameter
    ):
        # Filter by employee_id if not admin
        employee_id = None
        if not current_user.get("is_admin", False):
            employee_id = current_user.get("employee_id")  # atau sesuai nama field di JWT
        
        result = AttendanceService.get_all_attendance(db, page, perPage, search, employee_id)
        return handle_response(
            200,
            MESSAGE_CODE.SUCCESS,
            "Attendance records retrieved successfully",
            result["attendances"],
            meta=result["meta"]
        )

    @staticmethod
    async def get_attendance(
        attendance_id: int, 
        db: Session = Depends(get_db),
        current_user: dict = None  # Add this parameter
    ):
        # Filter by employee_id if not admin
        employee_id = None
        if not current_user.get("is_admin", False):
            employee_id = current_user.get("employee_id")
            
        attendance = AttendanceService.get_attendance_by_id(db, attendance_id, employee_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Attendance record retrieved successfully", attendance)

    @staticmethod
    async def delete_attendances(
        attendance_ids: List[int],
        db: Session = Depends(get_db)
    ):
        result = await AttendanceService.delete_multiple_attendances(db, attendance_ids)
        return handle_response(200, MESSAGE_CODE.SUCCESS, f"Successfully deleted {result['deleted_count']} attendance records", result)

    # @staticmethod
    # async def get_all_attendance(
    #     page: int = 1,
    #     perPage: int = 10,
    #     search: Optional[str] = None,
    #     db: Session = Depends(get_db)
    # ):
    #     result = AttendanceService.get_all_attendance(db, page, perPage, search)
    #     return handle_response(
    #         200,
    #         MESSAGE_CODE.SUCCESS,
    #         "Attendance records retrieved successfully",
    #         result["attendances"],
    #         meta=result["meta"]
    #     )
    
    # # @staticmethod
    # # async def get_all_attendance(
    # #     page: int = 1,
    # #     perPage: int = 10,
    # #     employee_id: Optional[int] = None,
    # #     start_date: Optional[date] = None,
    # #     end_date: Optional[date] = None,
    # #     db: Session = Depends(get_db)
    # # ):
    # #     result = AttendanceService.get_all_attendance(db, page, perPage, employee_id, start_date, end_date)
    # #     return handle_response(
    # #         200,
    # #         MESSAGE_CODE.SUCCESS,
    # #         "Attendance records retrieved successfully",
    # #         result["attendances"],
    # #         meta=result["meta"]
    # #     )

    # @staticmethod
    # async def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    #     attendance = AttendanceService.get_attendance_by_id(db, attendance_id)
    #     return handle_response(200, MESSAGE_CODE.SUCCESS, "Attendance record retrieved successfully", attendance)