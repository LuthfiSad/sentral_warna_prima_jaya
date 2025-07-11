# src/controllers/transaction_controller.py
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional
from src.services.transaction_service import TransactionService
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.schemas.transaction_schema import TransactionCalculateCostSchema, TransactionCreateSchema, TransactionUpdateSchema, TransactionStatusUpdateSchema
from src.config.database import get_db

class TransactionController:
    @staticmethod
    async def create_transaction(
        transaction_data: TransactionCreateSchema,
        current_user: dict,
        db: Session = Depends(get_db)
    ):
        print(current_user)
        """Admin buat transaksi perbaikan baru"""
        result = await TransactionService.create_transaction(db, transaction_data, current_user.get("user_id"))
        return handle_response(201, MESSAGE_CODE.CREATED, "Transaction created successfully", result)

    @staticmethod
    async def get_all_transactions(
        page: int = 1,
        perPage: int = 10,
        search: Optional[str] = None,
        status: Optional[str] = None,
        current_user: dict = None,
        db: Session = Depends(get_db)
    ):
        karyawan_id = None
        if not current_user.get("is_admin", False) and search != "selected":
            karyawan_id = current_user.get("karyawan_id")
            
        result = TransactionService.get_all_transactions(db, page, perPage, search, status, karyawan_id)
        return handle_response(
            200,
            MESSAGE_CODE.SUCCESS,
            "Transactions retrieved successfully",
            result["transactions"],
            meta=result["meta"]
        )

    @staticmethod
    async def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
        result = TransactionService.get_transaction_by_id(db, transaction_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Transaction retrieved successfully", result)

    @staticmethod
    async def update_transaction(
        transaction_id: int,
        transaction_data: TransactionUpdateSchema,
        current_user: dict,
        db: Session = Depends(get_db)
    ):
        result = await TransactionService.update_transaction(db, transaction_id, transaction_data, current_user.get("user_id"))
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Transaction updated successfully", result)

    @staticmethod
    async def update_transaction_status(
        transaction_id: int,
        status_data: TransactionStatusUpdateSchema,
        current_user: dict,
        db: Session = Depends(get_db)
    ):
        result = await TransactionService.update_transaction_status(
            db, transaction_id, status_data, current_user.get("user_id")
        )
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Transaction status updated successfully", result)

    @staticmethod
    async def start_work(
        transaction_id: int,
        current_user: dict,
        db: Session = Depends(get_db)
    ):
        """Karyawan mulai pengerjaan"""
        result = await TransactionService.start_work(db, transaction_id, current_user.get("user_id"))
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Work started successfully", result)

    @staticmethod
    async def calculate_total_cost(
        transaction_id: int,
        cost_data: TransactionCalculateCostSchema,
        current_user: dict,
        db: Session = Depends(get_db)
    ):
        """Admin input total cost untuk transaksi"""
        result = await TransactionService.calculate_total_cost(db, transaction_id, cost_data.total_cost, current_user)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Total cost calculated successfully", result)


    @staticmethod
    async def finalize_transaction(transaction_id: int, current_user: dict, db: Session = Depends(get_db)):
        """Admin finalize transaction ke status selesai"""
        result = await TransactionService.finalize_transaction(db, transaction_id, current_user)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Transaction finalized successfully", result)

    @staticmethod
    async def mark_as_paid(
        transaction_id: int,
        current_user: dict,
        db: Session = Depends(get_db)
    ):
        result = await TransactionService.mark_as_paid(db, transaction_id, current_user.get("user_id"))
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Transaction marked as paid successfully", result)

    @staticmethod
    async def get_transaction_history(transaction_id: int, db: Session = Depends(get_db)):
        result = TransactionService.get_transaction_history(db, transaction_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Transaction history retrieved successfully", result)