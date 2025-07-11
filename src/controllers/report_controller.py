# src/controllers/report_controller.py
from io import BytesIO
import pandas as pd
from fastapi import Depends, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from src.services.report_service import ReportService
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.config.database import get_db

class ReportController:
    @staticmethod
    async def create_draft_report(
        transaction_id: int,
        current_user: dict,
        description: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        image: Optional[UploadFile] = None,
        db: Session = Depends(get_db)
    ):
        """Karyawan buat draft laporan"""
        image_data = None
        if image:
            image_data = await image.read()
        
        result = await ReportService.create_draft_report(
            db, transaction_id, current_user, description, start_time, end_time, image_data
        )
        return handle_response(201, MESSAGE_CODE.CREATED, "Draft report created successfully", result)

    @staticmethod
    async def get_all_reports(
        page: int = 1,
        perPage: int = 10,
        search: Optional[str] = None,
        status: Optional[str] = None,
        transaction_id: Optional[int] = None,
        karyawan_id: Optional[int] = None,
        db: Session = Depends(get_db)
    ):
        result = ReportService.get_all_reports(db, page, perPage, search, status, transaction_id, karyawan_id)
        return handle_response(
            200,
            MESSAGE_CODE.SUCCESS,
            "Reports retrieved successfully",
            result["reports"],
            meta=result["meta"]
        )

    @staticmethod
    async def get_pending_reports(
        page: int = 1,
        perPage: int = 10,
        db: Session = Depends(get_db)
    ):
        """Get reports yang butuh approval"""
        result = ReportService.get_pending_reports(db, page, perPage)
        return handle_response(
            200,
            MESSAGE_CODE.SUCCESS,
            "Pending reports retrieved successfully",
            result["reports"],
            meta=result["meta"]
        )

    @staticmethod
    async def get_report(report_id: int, db: Session = Depends(get_db)):
        result = ReportService.get_report_by_id(db, report_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report retrieved successfully", result)

    @staticmethod
    async def update_report(
        report_id: int,
        employee_id: int,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        image: Optional[UploadFile] = None,
        db: Session = Depends(get_db)
    ):
        """Update draft report (hanya bisa edit draft/rejected)"""
        image_data = None
        if image:
            image_data = await image.read()
        
        result = await ReportService.update_report(
            db, report_id, employee_id, description, start_time, end_time, image_data
        )
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report updated successfully", result)

    @staticmethod
    async def submit_report(
        report_id: int,
        employee_id: int,
        db: Session = Depends(get_db)
    ):
        """Submit draft report untuk approval"""
        result = await ReportService.submit_report(db, report_id, employee_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report approved for approval", result)

    @staticmethod
    async def approve_report(
        report_id: int,
        approver_id: int,
        db: Session = Depends(get_db)
    ):
        """Admin approve report"""
        result = await ReportService.approve_report(db, report_id, approver_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report approved successfully", result)

    @staticmethod
    async def reject_report(
        report_id: int,
        approver_id: int,
        reason: str,
        db: Session = Depends(get_db)
    ):
        """Admin reject report dengan alasan"""
        result = await ReportService.reject_report(db, report_id, approver_id, reason)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report rejected successfully", result)

    @staticmethod
    async def delete_report(
        report_id: int,
        employee_id: int,
        db: Session = Depends(get_db)
    ):
        """Delete draft report"""
        result = ReportService.delete_report(db, report_id, employee_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report deleted successfully", result)

    @staticmethod
    async def get_transaction_reports(transaction_id: int, db: Session = Depends(get_db)):
        """Get all reports untuk suatu transaksi"""
        result = ReportService.get_transaction_reports(db, transaction_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Transaction reports retrieved successfully", result)

    @staticmethod
    async def export_reports_excel(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db)
    ):
        reports = ReportService.export_reports_excel(db, start_date, end_date, status)
        
        data = []
        for report in reports:
            data.append({
                'ID': report.id,
                'Transaction ID': report.transaction_id,
                'Employee ID': report.employee_id,
                'Employee Name': report.employee.name if report.employee else '',
                'Description': report.description,
                'Start Time': report.start_time.strftime('%Y-%m-%d %H:%M:%S') if report.start_time else '',
                'End Time': report.end_time.strftime('%Y-%m-%d %H:%M:%S') if report.end_time else '',
                'Status': report.status.value,
                'Approved By': report.approver.name if report.approver else '',
                'Approved At': report.approved_at.strftime('%Y-%m-%d %H:%M:%S') if report.approved_at else '',
                'Rejection Reason': report.rejection_reason or '',
                'Image URL': report.image_url or '',
                'Created At': report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Updated At': report.updated_at.strftime('%Y-%m-%d %H:%M:%S') if report.updated_at else ''
            })
        
        df = pd.DataFrame(data)
        
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Reports', index=False)
        
        excel_buffer.seek(0)
        
        filename = "reports_export"
        if start_date:
            filename += f"_from_{start_date}"
        if end_date:
            filename += f"_to_{end_date}"
        if status:
            filename += f"_status_{status}"
        filename += ".xlsx"
        
        return StreamingResponse(
            BytesIO(excel_buffer.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )