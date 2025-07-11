# src/services/history_service.py
from sqlalchemy.orm import Session
from typing import Optional
from src.repositories.history_repository import HistoryRepository
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.employee_repository import EmployeeRepository
from src.repositories.user_repository import UserRepository
from src.schemas.history_schema import HistoryCreateSchema
from src.models.transaction_model import TransactionStatus
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE

class HistoryService:
    @staticmethod
    async def create_history(
        db: Session, 
        history_data: HistoryCreateSchema, 
        created_by: Optional[int] = None
    ):
        """Create new history record"""
        try:
            # Verify transaction exists
            transaction = TransactionRepository.get_by_id(db, history_data.transaction_id)
            if not transaction:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Transaction not found")
            
            # Verify employee exists if created_by is provided
            if created_by:
                user = UserRepository.get_by_id(db, created_by)
                if not user:
                    raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "User not found")

            history = HistoryRepository.create(
                db, 
                history_data.transaction_id, 
                history_data.status, 
                history_data.note,
                created_by
            )
            
            return history
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to create history: {str(e)}")

    @staticmethod
    def get_transaction_history(db: Session, transaction_id: int):
        """Get all history records for a transaction"""
        # Verify transaction exists
        transaction = TransactionRepository.get_by_id(db, transaction_id)
        if not transaction:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Transaction not found")
        
        return HistoryRepository.get_by_transaction_id(db, transaction_id)

    @staticmethod
    def get_all_histories(
        db: Session, 
        page: int = 1, 
        perPage: int = 10, 
        transaction_id: Optional[int] = None,
        employee_id: Optional[int] = None
    ):
        """Get all history records with pagination and filtering"""
        return HistoryRepository.get_all(db, page, perPage, transaction_id, employee_id)

    @staticmethod
    def get_history_by_id(db: Session, history_id: int):
        """Get history by ID"""
        history = HistoryRepository.get_by_id(db, history_id)
        if not history:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "History record not found")
        return history

    @staticmethod
    def get_employee_activities(db: Session, employee_id: int, page: int = 1, perPage: int = 10):
        """Get all activities by specific employee"""
        # Verify employee exists
        employee = EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Employee not found")
        
        return HistoryRepository.get_by_employee_id(db, employee_id, page, perPage)

    @staticmethod
    def get_recent_activities(db: Session, limit: int = 10):
        """Get recent activities across all transactions"""
        return HistoryRepository.get_recent_activities(db, limit)