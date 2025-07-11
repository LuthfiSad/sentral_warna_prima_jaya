# src/routers/customer_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.controllers.customer_controller import CustomerController
from src.middlewares.catch_wrapper import catch_exceptions
from src.middlewares.admin_middleware import get_current_user, require_admin
from src.config.database import get_db
from src.schemas.customer_schema import CustomerCreateSchema, CustomerUpdateSchema

router = APIRouter()

@router.post("/")
@catch_exceptions
async def create_customer(
    customer_data: CustomerCreateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new customer"""
    return await CustomerController.create_customer(customer_data, db)

@router.get("/search/plate/{plate_number}")
@catch_exceptions
async def search_by_plate(
    plate_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Search customer by plate number (untuk scan plat nomor)"""
    return await CustomerController.get_customer_by_plate(plate_number, db)

@router.get("/")
@catch_exceptions
async def get_all_customers(
    page: int = Query(1, ge=1),
    perPage: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all customers with pagination and search"""
    return await CustomerController.get_all_customers(page, perPage, search, db)

@router.get("/{customer_id}")
@catch_exceptions
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get customer by ID"""
    return await CustomerController.get_customer(customer_id, db)

@router.put("/{customer_id}")
@catch_exceptions
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update customer data"""
    return await CustomerController.update_customer(customer_id, customer_data, db)

@router.delete("/{customer_id}")
@catch_exceptions
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """Delete customer (admin only)"""
    return await CustomerController.delete_customer(customer_id, db)

@router.get("/{customer_id}/transactions")
@catch_exceptions
async def get_customer_transactions(
    customer_id: int,
    page: int = Query(1, ge=1),
    perPage: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get customer transaction history"""
    return await CustomerController.get_customer_transactions(customer_id, page, perPage, db)