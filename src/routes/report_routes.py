# src/routers/report_router.py
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from src.controllers.report_controller import ReportController
from src.middlewares.catch_wrapper import catch_exceptions
from src.middlewares.admin_middleware import require_admin
from src.config.database import get_db

router = APIRouter()

@router.post("/")
@catch_exceptions
async def create_report(
    date: date = Form(...),
    name: str = Form(...),
    report: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    return await ReportController.create_report(date, name, report, image, db)

@router.get("/")
@catch_exceptions
async def get_all_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await ReportController.get_all_reports(page, per_page, search, db)

# Tambahan route untuk export excel di report_router.py
@router.get("/export/excel")
@catch_exceptions
async def export_reports_excel(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await ReportController.export_reports_excel(start_date, end_date, db)

# @router.get("/")
# @catch_exceptions
# async def get_all_reports(
#     page: int = Query(1, ge=1),
#     per_page: int = Query(10, ge=1, le=100),
#     status: Optional[str] = Query(None),
#     name: Optional[str] = Query(None),
#     start_date: Optional[date] = Query(None),
#     end_date: Optional[date] = Query(None),
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_admin)
# ):
#     return await ReportController.get_all_reports(
#         page, per_page, status, name, start_date, end_date, db
#     )

@router.get("/{report_id}")
@catch_exceptions
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await ReportController.get_report(report_id, db)

@router.put("/{report_id}")
@catch_exceptions
async def update_report(
    report_id: int,
    date: Optional[date] = Form(None),
    name: Optional[str] = Form(None),
    report: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    return await ReportController.update_report(report_id, date, name, report, image, db)

@router.delete("/{report_id}")
@catch_exceptions
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await ReportController.delete_report(report_id, db)

@router.patch("/{report_id}/approve")
@catch_exceptions
async def approve_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await ReportController.approve_report(report_id, db)

@router.patch("/{report_id}/reject")
@catch_exceptions
async def reject_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await ReportController.reject_report(report_id, db)