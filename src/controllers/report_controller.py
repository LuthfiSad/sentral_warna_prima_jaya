# src/controllers/report_controller.py
from io import BytesIO
import pandas as pd
from fastapi import Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from src.services.report_service import ReportService
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.config.database import get_db

class ReportController:
    @staticmethod
    async def create_report(
        date: date = Form(...),
        name: str = Form(...),
        report: str = Form(...),
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db)
    ):
        image_data = None
        if image:
            image_data = await image.read()
        
        result = await ReportService.create_report(db, date, name, report, image_data)
        return handle_response(201, MESSAGE_CODE.CREATED, "Report created successfully", result)

    @staticmethod
    async def get_all_reports(
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        db: Session = Depends(get_db)
    ):
        result = ReportService.get_all_reports(db, page, per_page, search)
        return handle_response(
            200,
            MESSAGE_CODE.SUCCESS,
            "Reports retrieved successfully",
            result["reports"],
            meta=result["meta"]
        )

    # Tambahan method untuk export excel di ReportController
    @staticmethod
    async def export_reports_excel(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = Depends(get_db)
    ):  
        reports = ReportService.export_reports_excel(db, start_date, end_date)
        
        # Convert to DataFrame
        data = []
        for report in reports:
            data.append({
                'ID': report.id,
                'Date': report.date.strftime('%Y-%m-%d'),
                'Name': report.name,
                'Report': report.report,
                'Status': report.status.value,
                'Image URL': report.image_url or '',
                'Created At': report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Updated At': report.updated_at.strftime('%Y-%m-%d %H:%M:%S') if report.updated_at else ''
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Reports', index=False)
        
        excel_buffer.seek(0)
        
        # Generate filename with date range
        filename = "reports_export"
        if start_date:
            filename += f"_from_{start_date.strftime('%Y%m%d')}"
        if end_date:
            filename += f"_to_{end_date.strftime('%Y%m%d')}"
        filename += ".xlsx"
        
        return StreamingResponse(
            BytesIO(excel_buffer.read()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    # @staticmethod
    # async def get_all_reports(
    #     page: int = 1,
    #     per_page: int = 10,
    #     status: Optional[str] = None,
    #     name: Optional[str] = None,
    #     start_date: Optional[date] = None,
    #     end_date: Optional[date] = None,
    #     db: Session = Depends(get_db)
    # ):
    #     result = ReportService.get_all_reports(db, page, per_page, status, name, start_date, end_date)
    #     return handle_response(
    #         200,
    #         MESSAGE_CODE.SUCCESS,
    #         "Reports retrieved successfully",
    #         result["reports"],
    #         meta=result["meta"]
    #     )

    @staticmethod
    async def get_report(report_id: int, db: Session = Depends(get_db)):
        report = ReportService.get_report_by_id(db, report_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report retrieved successfully", report)

    @staticmethod
    async def update_report(
        report_id: int,
        date: Optional[date] = Form(None),
        name: Optional[str] = Form(None),
        report: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db)
    ):
        image_data = None
        if image:
            image_data = await image.read()
        
        result = await ReportService.update_report(db, report_id, date, name, report, image_data)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report updated successfully", result)

    @staticmethod
    async def delete_report(report_id: int, db: Session = Depends(get_db)):
        result = ReportService.delete_report(db, report_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report deleted successfully", result)

    @staticmethod
    async def approve_report(report_id: int, db: Session = Depends(get_db)):
        result = ReportService.approve_report(db, report_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report approved successfully", result)

    @staticmethod
    async def reject_report(report_id: int, db: Session = Depends(get_db)):
        result = ReportService.reject_report(db, report_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Report rejected successfully", result)