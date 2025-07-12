# src/routers/report_router.py
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from src.controllers.report_controller import ReportController
from src.middlewares.catch_wrapper import catch_exceptions
from src.middlewares.admin_middleware import get_current_user, mush_not_admin_have_employee, require_admin
from src.config.database import get_db

router = APIRouter()

@router.post("/")
@catch_exceptions
async def create_pending_report(
    transaction_id: int = Form(...),
    description: str = Form(...),
    start_time: Optional[datetime] = Form(None),
    end_time: Optional[datetime] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(mush_not_admin_have_employee)
):
    """Karyawan buat pending laporan per pekerjaan"""
    return await ReportController.create_pending_report(
        transaction_id, current_user, 
        description, start_time, end_time, image, db
    )

@router.get("/")
@catch_exceptions
async def get_all_reports(
    page: int = Query(1, ge=1),
    perPage: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    transaction_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all reports with filtering"""
    karyawan_id = None
    if not current_user.get("is_admin", False):
        karyawan_id = current_user.get("karyawan_id")

    return await ReportController.get_all_reports(
        page, perPage, search, status, transaction_id, karyawan_id, db
    )

# @router.get("/pending-approval")
# @catch_exceptions
# async def get_pending_reports(
#     page: int = Query(1, ge=1),
#     perPage: int = Query(10, ge=1, le=100),
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_admin)
# ):
#     """Admin get reports yang butuh approval"""
#     return await ReportController.get_pending_reports(page, perPage, db)

@router.get("/{report_id}")
@catch_exceptions
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get report detail"""
    return await ReportController.get_report(report_id, db)

@router.put("/{report_id}")
@catch_exceptions
async def update_report(
    report_id: int,
    description: Optional[str] = Form(None),
    start_time: Optional[datetime] = Form(None),
    end_time: Optional[datetime] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(mush_not_admin_have_employee)
):
    """Karyawan update pending report (hanya bisa edit pending/rejected)"""
    return await ReportController.update_report(
        report_id, current_user.get("karyawan_id"),
        description, start_time, end_time, image, db
    )

@router.post("/{report_id}/submit")
@catch_exceptions
async def submit_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(mush_not_admin_have_employee)
):
    """Karyawan submit pending report untuk approval"""
    return await ReportController.submit_report(
        report_id, current_user.get("karyawan_id"), db
    )

@router.post("/{report_id}/approve")
@catch_exceptions
async def approve_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Admin approve report"""
    return await ReportController.approve_report(
        report_id, current_user, db
    )

@router.post("/{report_id}/reject")
@catch_exceptions
async def reject_report(
    report_id: int,
    reason: str = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Admin reject report dengan alasan"""
    return await ReportController.reject_report(
        report_id, current_user, reason, db
    )

@router.delete("/{report_id}")
@catch_exceptions
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(mush_not_admin_have_employee)
):
    """Delete pending report (hanya bisa delete pending)"""
    return await ReportController.delete_report(
        report_id, current_user.get("karyawan_id"), db
    )

@router.get("/transaction/{transaction_id}")
@catch_exceptions
async def get_transaction_reports(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all reports for a transaction"""
    return await ReportController.get_transaction_reports(transaction_id, db)

@router.get("/export/excel")
@catch_exceptions
async def export_reports_excel(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Export reports to Excel"""
    return await ReportController.export_reports_excel(start_date, end_date, status, db)