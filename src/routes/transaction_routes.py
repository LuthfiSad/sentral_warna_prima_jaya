# src/routers/transaction_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.controllers.transaction_controller import TransactionController
from src.middlewares.catch_wrapper import catch_exceptions
from src.middlewares.admin_middleware import get_current_user, require_admin
from src.config.database import get_db
from src.schemas.transaction_schema import (
    TransactionCalculateCostSchema,
    TransactionCreateSchema, 
    TransactionUpdateSchema, 
    TransactionStatusUpdateSchema
)

router = APIRouter()

@router.post("/")
@catch_exceptions
async def create_transaction(
    transaction_data: TransactionCreateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Admin buat transaksi perbaikan baru"""
    return await TransactionController.create_transaction(transaction_data, current_user, db)

@router.get("/")
@catch_exceptions
async def get_all_transactions(
    page: int = Query(1, ge=1),
    perPage: int = Query(10, ge=1, le=9999999999),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all transactions with filtering"""
    return await TransactionController.get_all_transactions(
        page, perPage, search, status, current_user, db
    )

@router.get("/{transaction_id}")
@catch_exceptions
async def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get transaction detail with reports"""
    return await TransactionController.get_transaction(transaction_id, db)

@router.put("/{transaction_id}")
@catch_exceptions
async def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update transaction data"""
    return await TransactionController.update_transaction(
        transaction_id, transaction_data, current_user, db
    )

@router.patch("/{transaction_id}/status")
@catch_exceptions
async def update_transaction_status(
    transaction_id: int,
    status_data: TransactionStatusUpdateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update transaction status"""
    return await TransactionController.update_transaction_status(
        transaction_id, status_data, current_user, db
    )

@router.post("/{transaction_id}/start-work")
@catch_exceptions
async def start_work(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Karyawan mulai pengerjaan (status: proses)"""
    return await TransactionController.start_work(transaction_id, current_user, db)

@router.post("/{transaction_id}/calculate-cost")
@catch_exceptions
async def calculate_total_cost(
    transaction_id: int,
    cost_data: TransactionCalculateCostSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Admin input total cost from approved reports"""
    return await TransactionController.calculate_total_cost(transaction_id, cost_data, current_user, db)

@router.post("/{transaction_id}/finalize")
@catch_exceptions
async def finalize_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Admin finalize transaction to 'selesai' status"""
    return await TransactionController.finalize_transaction(transaction_id, current_user, db)

@router.post("/{transaction_id}/mark-paid")
@catch_exceptions
async def mark_as_paid(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark transaction as paid"""
    return await TransactionController.mark_as_paid(transaction_id, current_user, db)

@router.get("/{transaction_id}/history")
@catch_exceptions
async def get_transaction_history(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get transaction status history"""
    return await TransactionController.get_transaction_history(transaction_id, db)