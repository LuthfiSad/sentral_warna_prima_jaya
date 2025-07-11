# src/services/report_service.py
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from src.repositories.report_repository import ReportRepository
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.employee_repository import EmployeeRepository
from src.repositories.history_repository import HistoryRepository
from src.models.report_model import ReportStatus
from src.models.transaction_model import TransactionStatus
from src.libs.supabase import upload_image_to_supabase
from src.repositories.user_repository import UserRepository
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE

class ReportService:
    @staticmethod
    async def create_draft_report(
        db: Session, 
        transaction_id: int,
        current_user: dict, 
        description: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        image_data: bytes = None
    ):
        """Karyawan buat draft laporan"""
        try:
            # Verify transaction exists and is in progress
            transaction = TransactionRepository.get_by_id(db, transaction_id)
            if not transaction:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Transaction not found")
            
            if transaction.status not in [TransactionStatus.PENDING, TransactionStatus.PROSES]:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Cannot create report for this transaction status")

            # If transaction is pending, automatically start work
            if transaction.status == TransactionStatus.PENDING:
                TransactionRepository.update_status(db, transaction_id, TransactionStatus.PROSES.value)
                HistoryRepository.create(
                    db, transaction_id, TransactionStatus.PROSES.value, 
                    f"Work started automatically when creating first report", current_user.get("user_id")
                )

            # Verify employee exists
            employee = EmployeeRepository.get_by_id(db, current_user.get("karyawan_id"))
            if not employee:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "User not found")

            image_url = None
            if image_data:
                image_url = await upload_image_to_supabase(image_data)
                if isinstance(image_url, AppError):
                    raise image_url

            report = ReportRepository.create_draft(
                db, transaction_id, current_user.get("karyawan_id"), description, 
                start_time, end_time, image_url
            )
            
            return report
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to create draft report: {str(e)}")

    @staticmethod
    def get_all_reports(db: Session, page: int = 1, perPage: int = 10, search: str = None, status: str = None, transaction_id: int = None, karyawan_id: Optional[int] = None):
        """Get all reports with filtering"""
        return ReportRepository.get_all(db, page, perPage, search, status, transaction_id, karyawan_id)

    @staticmethod
    def get_pending_reports(db: Session, page: int = 1, perPage: int = 10):
        """Get reports yang butuh approval"""
        return ReportRepository.get_pending_approval(db, page, perPage)

    @staticmethod
    def get_report_by_id(db: Session, report_id: int):
        """Get report by ID"""
        report = ReportRepository.get_by_id(db, report_id)
        if not report:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Report not found")
        return report

    @staticmethod
    async def update_report(
        db: Session, 
        report_id: int,
        employee_id: int,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        image_data: bytes = None
    ):
        """Update draft report (hanya bisa edit draft/rejected)"""
        try:
            existing_report = ReportRepository.get_by_id(db, report_id)
            if not existing_report:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Report not found")

            # Check ownership
            if existing_report.employee_id != employee_id:
                raise AppError(403, MESSAGE_CODE.FORBIDDEN, "You can only edit your own reports")

            # Only allow editing draft or rejected reports
            if existing_report.status not in [ReportStatus.DRAFT, ReportStatus.REJECTED]:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Can only edit draft or rejected reports")

            image_url = existing_report.image_url
            if image_data:
                image_url = await upload_image_to_supabase(image_data)
                if isinstance(image_url, AppError):
                    raise image_url

            # Reset status to draft if it was rejected
            new_status = ReportStatus.DRAFT

            updated_report = ReportRepository.update(
                db, report_id,
                description=description,
                start_time=start_time,
                end_time=end_time,
                image_url=image_url,
                status=new_status,
                rejection_reason=None  # Clear rejection reason
            )
            
            return updated_report
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to update report: {str(e)}")

    @staticmethod
    async def submit_report(db: Session, report_id: int, employee_id: int):
        """Submit draft report untuk approval"""
        try:
            report = ReportRepository.get_by_id(db, report_id)
            if not report:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Report not found")

            # Check ownership
            if report.employee_id != employee_id:
                raise AppError(403, MESSAGE_CODE.FORBIDDEN, "You can only submit your own reports")

            if report.status != ReportStatus.DRAFT:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Only draft reports can be submitted")

            updated_report = ReportRepository.update_status(db, report_id, ReportStatus.SUBMITTED.value)
            
            # Update transaction status if needed
            transaction = TransactionRepository.get_by_id(db, report.transaction_id)
            user = UserRepository.get_by_employee_id(db, employee_id)
            if not user:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "User not found")
            if transaction.status == TransactionStatus.PROSES:
                TransactionRepository.update_status(db, report.transaction_id, TransactionStatus.MENUNGGU_APPROVAL)
                HistoryRepository.create(
                    db, report.transaction_id, TransactionStatus.MENUNGGU_APPROVAL.value, 
                    f"Report submitted for approval", user.id
                )
            
            return updated_report
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to submit report: {str(e)}")

    @staticmethod
    async def approve_report(db: Session, report_id: int, approver_id: int):
        """Admin approve report"""
        try:
            report = ReportRepository.get_by_id(db, report_id)
            if not report:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Report not found")

            if report.status != ReportStatus.SUBMITTED:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Only submitted reports can be approved")

            updated_report = ReportRepository.approve(db, report_id, approver_id)
            
            return updated_report
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to approve report: {str(e)}")

    @staticmethod
    async def reject_report(db: Session, report_id: int, approver_id: int, reason: str):
        """Admin reject report dengan alasan"""
        try:
            report = ReportRepository.get_by_id(db, report_id)
            if not report:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Report not found")

            if report.status != ReportStatus.SUBMITTED:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Only submitted reports can be rejected")

            updated_report = ReportRepository.reject(db, report_id, approver_id, reason)
            
            return updated_report
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to reject report: {str(e)}")

    @staticmethod
    def delete_report(db: Session, report_id: int, employee_id: int):
        """Delete draft report"""
        existing_report = ReportRepository.get_by_id(db, report_id)
        if not existing_report:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Report not found")

        # Check ownership
        if existing_report.employee_id != employee_id:
            raise AppError(403, MESSAGE_CODE.FORBIDDEN, "You can only delete your own reports")

        # Only allow deleting draft reports
        if existing_report.status != ReportStatus.DRAFT:
            raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Only draft reports can be deleted")

        success = ReportRepository.delete(db, report_id)
        if not success:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, "Failed to delete report")
        
        return {"message": "Report deleted successfully"}

    @staticmethod
    def get_transaction_reports(db: Session, transaction_id: int):
        """Get all reports untuk suatu transaksi"""
        return ReportRepository.get_by_transaction_id(db, transaction_id)

    @staticmethod
    def export_reports_excel(db: Session, start_date: Optional[str] = None, end_date: Optional[str] = None, status: Optional[str] = None):
        """Export reports to Excel"""
        return ReportRepository.get_all_for_export(db, start_date, end_date, status)