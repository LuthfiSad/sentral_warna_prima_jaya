# src/services/customer_service.py
from sqlalchemy.orm import Session
from typing import Optional
from src.repositories.customer_repository import CustomerRepository
from src.schemas.customer_schema import CustomerCreateSchema, CustomerUpdateSchema
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE

class CustomerService:
    @staticmethod
    async def create_customer(db: Session, customer_data: CustomerCreateSchema):
        """Create new customer"""
        try:
            # Check if plate number already exists
            existing_customer = CustomerRepository.get_by_plate_number(db, customer_data.plate_number)
            if existing_customer:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Plate number already exists")
            
            customer = CustomerRepository.create(db, customer_data)
            return customer
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to create customer: {str(e)}")

    @staticmethod
    def get_customer_by_plate(db: Session, plate_number: str):
        """Search customer by plate number"""
        return CustomerRepository.get_by_plate_number(db, plate_number.upper())

    @staticmethod
    def get_all_customers(db: Session, page: int = 1, per_page: int = 10, search: str = None):
        return CustomerRepository.get_all(db, page, per_page, search)

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int):
        customer = CustomerRepository.get_by_id(db, customer_id)
        if not customer:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Customer not found")
        return customer

    @staticmethod
    async def update_customer(db: Session, customer_id: int, customer_data: CustomerUpdateSchema):
        try:
            existing_customer = CustomerRepository.get_by_id(db, customer_id)
            if not existing_customer:
                raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Customer not found")

            updated_customer = CustomerRepository.update(db, customer_id, customer_data)
            return updated_customer
        except AppError:
            raise
        except Exception as e:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, f"Failed to update customer: {str(e)}")

    @staticmethod
    def delete_customer(db: Session, customer_id: int):
        existing_customer = CustomerRepository.get_by_id(db, customer_id)
        if not existing_customer:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Customer not found")

        success = CustomerRepository.delete(db, customer_id)
        if not success:
            raise AppError(500, MESSAGE_CODE.INTERNAL_SERVER_ERROR, "Failed to delete customer")
        
        return {"message": "Customer deleted successfully"}

    @staticmethod
    def get_customer_transactions(db: Session, customer_id: int, page: int = 1, per_page: int = 10):
        return CustomerRepository.get_customer_transactions(db, customer_id, page, per_page)
