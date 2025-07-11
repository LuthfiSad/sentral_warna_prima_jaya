# src/routers/history_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.controllers.history_controller import HistoryController
from src.middlewares.catch_wrapper import catch_exceptions
from src.middlewares.admin_middleware import get_current_user, require_admin
from src.config.database import get_db
from src.schemas.history_schema import HistoryCreateSchema

router = APIRouter()

@router.get("/")
@catch_exceptions
async def get_all_histories(
    page: int = Query(1, ge=1),
    perPage: int = Query(10, ge=1, le=100),
    transaction_id: Optional[int] = Query(None),
    employee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all history records with filtering"""
    return await HistoryController.get_all_histories(
        page, perPage, transaction_id, employee_id, current_user, db
    )

@router.get("/recent")
@catch_exceptions
async def get_recent_activities(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get recent activities for dashboard"""
    return await HistoryController.get_recent_activities(limit, db)

@router.get("/transaction/{transaction_id}")
@catch_exceptions
async def get_transaction_history(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get specific transaction history"""
    return await HistoryController.get_transaction_history(transaction_id, db)

@router.get("/employee/{employee_id}")
@catch_exceptions
async def get_employee_activities(
    employee_id: int,
    page: int = Query(1, ge=1),
    perPage: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get specific employee activities"""
    return await HistoryController.get_employee_activities(employee_id, page, perPage, db)

@router.get("/{history_id}")
@catch_exceptions
async def get_history(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get history detail by ID"""
    return await HistoryController.get_history(history_id, db)
