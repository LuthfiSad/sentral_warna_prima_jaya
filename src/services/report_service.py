# src/services/report_service.py
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from src.repositories.employee_repository import EmployeeRepository
from src.repositories.report_repository import ReportRepository
from src.models.report_model import ReportStatus
from src.libs.supabase import upload_image_to_supabase
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE

class ReportService:
    @staticmethod
    async def create_report(
        db: Session, 
        report_date: date, 
        employee_id: int, 
        report: str, 
        customer_name: str,
        vehicle_type: str,
        total_repairs: int,
        cost: float,
        image_data: bytes = None
    ):
        """
        Create new report
        """
        try:
            employee = EmployeeRepository.get_by_id(db, employee_id)
            if not employee:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Employee not found")
            
            image_url = None
            if image_data:
                image_url = await upload_image_to_supabase(image_data)
                if isinstance(image_url, AppError):
                    raise image_url

            report_record = ReportRepository.create(
                db, report_date, employee_id, report, customer_name,
                vehicle_type, total_repairs, cost, image_url, ReportStatus.PENDING
            )
            
            return report_record

        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to create report: {str(e)}")

    @staticmethod
    def get_all_reports(db: Session, page: int = 1, per_page: int = 10, search: str = None, karyawan_id: Optional[str] = None):
        return ReportRepository.get_all(db, page, per_page, search, karyawan_id)

    @staticmethod
    def export_reports_excel(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None):
        return ReportRepository.get_all_for_export(db, start_date, end_date)

    @staticmethod
    def get_report_by_id(db: Session, report_id: int):
        """
        Get report by ID
        """
        report = ReportRepository.get_by_id(db, report_id)
        if not report:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Report not found")
        return report

    @staticmethod
    async def update_report(
        db: Session, 
        report_id: int, 
        report_date: Optional[date] = None,
        report: Optional[str] = None,
        customer_name: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        total_repairs: Optional[int] = None,
        cost: Optional[float] = None,
        image_data: bytes = None
    ):
        """
        Update existing report
        """
        try:
            existing_report = ReportRepository.get_by_id(db, report_id)
            if not existing_report:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Report not found")

            new_status = existing_report.status
            if existing_report.status == ReportStatus.REJECTED or existing_report.status == ReportStatus.APPROVED:
                new_status = ReportStatus.PENDING
            # Only allow updates if status is pending
            elif existing_report.status != ReportStatus.PENDING:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Cannot update approved/rejected reports")

            image_url = existing_report.image_url
            if image_data:
                image_url = await upload_image_to_supabase(image_data)
                if isinstance(image_url, AppError):
                    raise image_url

            updated_report = ReportRepository.update(
                db, report_id,
                date=report_date, 
                report=report,
                customer_name=customer_name,
                vehicle_type=vehicle_type,
                total_repairs=total_repairs,
                cost=cost,
                status=new_status,
                image_url=image_url
            )
            
            return updated_report

        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to update report: {str(e)}")

    @staticmethod
    def delete_report(db: Session, report_id: int):
        """
        Delete report (only if pending)
        """
        existing_report = ReportRepository.get_by_id(db, report_id)
        if not existing_report:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Report not found")

        success = ReportRepository.delete(db, report_id)
        if not success:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, "Failed to delete report")
        
        return {"message": "Report deleted successfully"}
    
    @staticmethod
    def update_report_status(db: Session, report_id: int, action: str):
        report = ReportRepository.get_by_id(db, report_id)
        if not report:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Report not found")

        if report.status != ReportStatus.PENDING:
            raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Report is not in pending status")

        if action == "approve":
            new_status = ReportStatus.APPROVED
        elif action == "reject":
            new_status = ReportStatus.REJECTED
        else:
            raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Invalid action")

        updated_report = ReportRepository.update_status(db, report_id, new_status)
        return updated_report