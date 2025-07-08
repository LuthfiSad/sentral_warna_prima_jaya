# src/routers/report_router.py
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from src.controllers.report_controller import ReportController
from src.middlewares.catch_wrapper import catch_exceptions
from src.middlewares.admin_middleware import get_current_user, mush_not_admin_have_employee, require_admin
from src.config.database import get_db
from src.middlewares.jwt_auth_middleware import get_current_user_or_none
from src.schemas.export_schema import StatusUpdateSchema

router = APIRouter()

@router.post("/")
@catch_exceptions
async def create_report(
    date: date = Form(...),
    report: str = Form(...),
    customer_name: str = Form(...),
    vehicle_type: str = Form(...),
    total_repairs: int = Form(...),
    cost: float = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(mush_not_admin_have_employee)
):
    return await ReportController.create_report(
        date, current_user.get("karyawan_id"), report, 
        customer_name, vehicle_type, total_repairs, cost, image, db
    )

@router.get("/")
@catch_exceptions
async def get_all_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    karyawan_id = None
    if not current_user.get("is_admin", False):
        karyawan_id = current_user.get("karyawan_id")

    return await ReportController.get_all_reports(page, per_page, search, karyawan_id, db)

@router.get("/export/excel")
@catch_exceptions
async def export_reports_excel(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await ReportController.export_reports_excel(start_date, end_date, db)

@router.get("/{report_id}")
@catch_exceptions
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(require_admin)
):
    return await ReportController.get_report(report_id, db)

@router.put("/{report_id}")
@catch_exceptions
async def update_report(
    report_id: int,
    date: Optional[date] = Form(None),
    report: Optional[str] = Form(None),
    customer_name: Optional[str] = Form(None),
    vehicle_type: Optional[str] = Form(None),
    total_repairs: Optional[int] = Form(None),
    cost: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    return await ReportController.update_report(
        report_id, date, report, customer_name, vehicle_type, 
        total_repairs, cost, image, db
    )

@router.delete("/{report_id}")
@catch_exceptions
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
):
    return await ReportController.delete_report(report_id, db)

@router.patch("/{report_id}/status")
@catch_exceptions
async def update_report_status(
    report_id: int,
    body: StatusUpdateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await ReportController.update_report_status(report_id, body.status, db)