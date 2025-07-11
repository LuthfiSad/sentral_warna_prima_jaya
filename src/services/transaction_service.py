# src/services/transaction_service.py
from sqlalchemy.orm import Session
from typing import Optional
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.history_repository import HistoryRepository
from src.repositories.report_repository import ReportRepository
from src.schemas.transaction_schema import TransactionCreateSchema, TransactionUpdateSchema, TransactionStatusUpdateSchema
from src.models.transaction_model import TransactionStatus
from src.models.report_model import ReportStatus
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE

class TransactionService:
    @staticmethod
    async def create_transaction(db: Session, transaction_data: TransactionCreateSchema, created_by: int):
        """Admin buat transaksi perbaikan baru"""
        try:
            # Verify customer exists
            customer = CustomerRepository.get_by_id(db, transaction_data.customer_id)
            if not customer:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Customer not found")
            
            transaction = TransactionRepository.create(db, transaction_data)
            
            # Create history record
            HistoryRepository.create(
                db, transaction.id, TransactionStatus.PENDING.value, 
                f"Transaction created by admin", created_by
            )
            
            return transaction
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to create transaction: {str(e)}")

    @staticmethod
    def get_all_transactions(db: Session, page: int = 1, perPage: int = 10, search: str = None, status: str = None, karyawan_id: Optional[int] = None):
        return TransactionRepository.get_all(db, page, perPage, search, status, karyawan_id)

    @staticmethod
    def get_transaction_by_id(db: Session, transaction_id: int):
        transaction = TransactionRepository.get_by_id(db, transaction_id)
        if not transaction:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Transaction not found")
        return transaction

    @staticmethod
    async def update_transaction(db: Session, transaction_id: int, transaction_data: TransactionUpdateSchema, updated_by: int):
        try:
            existing_transaction = TransactionRepository.get_by_id(db, transaction_id)
            if not existing_transaction:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Transaction not found")

            updated_transaction = TransactionRepository.update(db, transaction_id, transaction_data)
            
            # Create history record
            HistoryRepository.create(
                db, transaction_id, existing_transaction.status, 
                f"Transaction updated", updated_by
            )
            
            return updated_transaction
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to update transaction: {str(e)}")

    @staticmethod
    async def update_transaction_status(db: Session, transaction_id: int, status_data: TransactionStatusUpdateSchema, updated_by: int):
        try:
            transaction = TransactionRepository.get_by_id(db, transaction_id)
            if not transaction:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Transaction not found")

            updated_transaction = TransactionRepository.update_status(db, transaction_id, status_data.status)
            
            # Create history record
            note = status_data.note or f"Status changed to {status_data.status.value}"
            HistoryRepository.create(
                db, transaction_id, status_data.status, note, updated_by
            )
            
            return updated_transaction
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to update transaction status: {str(e)}")

    @staticmethod
    async def start_work(db: Session, transaction_id: int, employee_id: int):
        """Karyawan mulai pengerjaan - status menjadi proses"""
        try:
            transaction = TransactionRepository.get_by_id(db, transaction_id)
            if not transaction:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Transaction not found")

            if transaction.status != TransactionStatus.PENDING:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Transaction is not in pending status")

            updated_transaction = TransactionRepository.update_status(db, transaction_id, TransactionStatus.PROSES)
            
            # Create history record
            HistoryRepository.create(
                db, transaction_id, TransactionStatus.PROSES, 
                f"Work started by employee", employee_id
            )
            
            return updated_transaction
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to start work: {str(e)}")

    @staticmethod
    async def calculate_total_cost(db: Session, transaction_id: int, total_cost: float, current_user: dict):
        """Admin input total cost untuk transaksi"""
        try:
            transaction = TransactionRepository.get_by_id(db, transaction_id)
            if not transaction:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Transaction not found")

            # Check if transaction has approved reports
            approved_reports = ReportRepository.get_approved_reports_by_transaction(db, transaction_id)
            
            if not approved_reports:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "No approved reports found for this transaction")

            # Update transaction with input total cost
            updated_transaction = TransactionRepository.update_cost(db, transaction_id, total_cost)
            # Create history record
            HistoryRepository.create(
                db, transaction_id, transaction.status.value, 
                f"Total cost calculated: Rp {total_cost:,.0f}", current_user.get("user_id")
            )
            
            return updated_transaction
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to calculate total cost: {str(e)}")

    @staticmethod
    async def finalize_transaction(db: Session, transaction_id: int, current_user: dict):
        """Admin finalize transaction ke status selesai"""
        try:
            transaction = TransactionRepository.get_by_id(db, transaction_id)
            if not transaction:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Transaction not found")

            # Check if all reports are approved
            pending_reports = ReportRepository.get_pending_reports_by_transaction(db, transaction_id)
            if pending_reports:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Cannot finalize transaction with pending reports")

            if not transaction.total_cost:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Total cost must be calculated before finalizing")

            updated_transaction = TransactionRepository.update_status(db, transaction_id, TransactionStatus.SELESAI.value)
            
            # Create history record
            HistoryRepository.create(
                db, transaction_id, TransactionStatus.SELESAI.value, 
                f"Transaction finalized", current_user.get("user_id")
            )
            
            return updated_transaction
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to finalize transaction: {str(e)}")

    @staticmethod
    async def mark_as_paid(db: Session, transaction_id: int, marked_by: int):
        """Mark transaction as paid"""
        try:
            transaction = TransactionRepository.get_by_id(db, transaction_id)
            if not transaction:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Transaction not found")

            if transaction.status != TransactionStatus.SELESAI:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Transaction must be completed before marking as paid")

            updated_transaction = TransactionRepository.update_status(db, transaction_id, TransactionStatus.DIBAYAR.value)
            
            # Create history record
            HistoryRepository.create(
                db, transaction_id, TransactionStatus.DIBAYAR.value, 
                f"Payment received", marked_by
            )
            
            return updated_transaction
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to mark as paid: {str(e)}")

    @staticmethod
    def get_transaction_history(db: Session, transaction_id: int):
        return HistoryRepository.get_by_transaction_id(db, transaction_id)
