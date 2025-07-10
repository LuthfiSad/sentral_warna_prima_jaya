# src/controllers/customer_controller.py
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional
from src.services.customer_service import CustomerService
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.schemas.customer_schema import CustomerCreateSchema, CustomerUpdateSchema
from src.config.database import get_db

class CustomerController:
    @staticmethod
    async def create_customer(
        customer_data: CustomerCreateSchema,
        db: Session = Depends(get_db)
    ):
        result = await CustomerService.create_customer(db, customer_data)
        return handle_response(201, MESSAGE_CODE.CREATED, "Customer created successfully", result)

    @staticmethod
    async def get_customer_by_plate(
        plate_number: str,
        db: Session = Depends(get_db)
    ):
        """Search customer by plate number - untuk scan plat nomor"""
        result = CustomerService.get_customer_by_plate(db, plate_number)
        if result:
            return handle_response(200, MESSAGE_CODE.SUCCESS, "Customer found", result)
        else:
            return handle_response(404, MESSAGE_CODE.NOT_FOUND, "Customer not found", None)

    @staticmethod
    async def get_all_customers(
        page: int = 1,
        per_page: int = 10,
        search: Optional[str] = None,
        db: Session = Depends(get_db)
    ):
        result = CustomerService.get_all_customers(db, page, per_page, search)
        return handle_response(
            200,
            MESSAGE_CODE.SUCCESS,
            "Customers retrieved successfully",
            result["customers"],
            meta=result["meta"]
        )

    @staticmethod
    async def get_customer(customer_id: int, db: Session = Depends(get_db)):
        result = CustomerService.get_customer_by_id(db, customer_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Customer retrieved successfully", result)

    @staticmethod
    async def update_customer(
        customer_id: int,
        customer_data: CustomerUpdateSchema,
        db: Session = Depends(get_db)
    ):
        result = await CustomerService.update_customer(db, customer_id, customer_data)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Customer updated successfully", result)

    @staticmethod
    async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
        result = CustomerService.delete_customer(db, customer_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Customer deleted successfully", result)

    @staticmethod
    async def get_customer_transactions(
        customer_id: int,
        page: int = 1,
        per_page: int = 10,
        db: Session = Depends(get_db)
    ):
        result = CustomerService.get_customer_transactions(db, customer_id, page, per_page)
        return handle_response(
            200,
            MESSAGE_CODE.SUCCESS,
            "Customer transactions retrieved successfully",
            result["transactions"],
            meta=result["meta"]
        )
