# src/routers/attendance_router.py
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from src.controllers.attendance_controller import AttendanceController
from src.middlewares.catch_wrapper import catch_exceptions
from src.middlewares.admin_middleware import require_admin
from src.config.database import get_db

router = APIRouter()

@router.post("/checkin")
@catch_exceptions
async def checkin(
    image: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    employee_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    return await AttendanceController.checkin(image, latitude, longitude, employee_id, db)

@router.post("/checkout")
@catch_exceptions
async def checkout(
    image: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    employee_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    return await AttendanceController.checkout(image, latitude, longitude, employee_id, db)

@router.get("/")
@catch_exceptions
async def get_all_attendance(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await AttendanceController.get_all_attendance(page, per_page, search, db)

@router.get("/{attendance_id}")
@catch_exceptions
async def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await AttendanceController.get_attendance(attendance_id, db)