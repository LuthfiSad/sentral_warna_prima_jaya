# src/controllers/history_controller.py
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional
from src.services.history_service import HistoryService
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.schemas.history_schema import HistoryCreateSchema
from src.config.database import get_db

class HistoryController:
    @staticmethod
    async def create_history(
        history_data: HistoryCreateSchema,
        current_user: dict,
        db: Session = Depends(get_db)
    ):
        """Create new history record"""
        result = await HistoryService.create_history(
            db, history_data, current_user.get("user_id")
        )
        return handle_response(201, MESSAGE_CODE.CREATED, "History record created successfully", result)

    @staticmethod
    async def get_transaction_history(
        transaction_id: int, 
        db: Session = Depends(get_db)
    ):
        """Get transaction history"""
        result = HistoryService.get_transaction_history(db, transaction_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Transaction history retrieved successfully", result)

    @staticmethod
    async def get_all_histories(
        page: int = 1,
        perPage: int = 10,
        transaction_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        current_user: dict = None,
        db: Session = Depends(get_db)
    ):
        """Get all histories with filtering"""
        # If not admin, filter by own employee_id
        if not current_user.get("is_admin", False) and not employee_id:
            employee_id = current_user.get("user_id")
            
        result = HistoryService.get_all_histories(db, page, perPage, transaction_id, employee_id)
        return handle_response(
            200,
            MESSAGE_CODE.SUCCESS,
            "Histories retrieved successfully",
            result["histories"],
            meta=result["meta"]
        )

    @staticmethod
    async def get_history(history_id: int, db: Session = Depends(get_db)):
        """Get history by ID"""
        result = HistoryService.get_history_by_id(db, history_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "History retrieved successfully", result)

    @staticmethod
    async def get_employee_activities(
        employee_id: int,
        page: int = 1,
        perPage: int = 10,
        db: Session = Depends(get_db)
    ):
        """Get employee activities"""
        result = HistoryService.get_employee_activities(db, employee_id, page, perPage)
        return handle_response(
            200,
            MESSAGE_CODE.SUCCESS,
            "Employee activities retrieved successfully",
            result["histories"],
            meta=result["meta"]
        )

    @staticmethod
    async def get_recent_activities(
        limit: int = 10,
        db: Session = Depends(get_db)
    ):
        """Get recent activities for dashboard"""
        result = HistoryService.get_recent_activities(db, limit)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Recent activities retrieved successfully", result)
