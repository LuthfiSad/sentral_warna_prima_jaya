from sqlalchemy.orm import Session
from src.repositories.employee_repository import EmployeeRepository
from src.libs.supabase import upload_image_to_supabase
from src.utils.error import AppError
from src.utils.message_code import MESSAGE_CODE
from typing import Optional, List

class EmployeeService:
    # @staticmethod
    # def get_all_employees(db: Session, skip: int = 0, limit: int = 100) -> List:
    #     return EmployeeRepository.get_all(db, skip, limit)
    
    @staticmethod
    def get_all_employees(db: Session, page: int = 1, per_page: int = 10, search: str = None):
        return EmployeeRepository.get_all(db, page, per_page, search)

    @staticmethod
    def get_employee_by_id(db: Session, employee_id: int):
        employee = EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Employee not found")
        return employee

    @staticmethod
    async def create_employee(db: Session, name: str, email: str, date_of_birth, divisi: str, address: str, image_data: bytes = None):
        # Check if email already exists
        if EmployeeRepository.get_by_email(db, email):
            raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Email already exists")

        image_url = None
        if image_data:
            image_url = await upload_image_to_supabase(image_data)
            if isinstance(image_url, AppError):
                raise image_url

        employee = EmployeeRepository.create(db, name, email, date_of_birth, divisi, address, image_url)
        return employee

    @staticmethod
    async def update_employee(db: Session, employee_id: int, name: str = None, email: str = None, 
                            date_of_birth=None, divisi: str = None, address: str = None, image_data: bytes = None):
        employee = EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Employee not found")

        # Check if email already exists (but not for current employee)
        if email and email != employee.email:
            existing_employee = EmployeeRepository.get_by_email(db, email)
            if existing_employee:
                raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Email already exists")

        image_url = employee.image_url
        if image_data:
            image_url = await upload_image_to_supabase(image_data)
            if isinstance(image_url, AppError):
                raise image_url

        updated_employee = EmployeeRepository.update(
            db, employee_id,
            name=name, email=email, date_of_birth=date_of_birth,
            divisi=divisi, address=address, image_url=image_url
        )
        return updated_employee

    @staticmethod
    def delete_employee(db: Session, employee_id: int):
        employee = EmployeeRepository.get_by_id(db, employee_id)
        if not employee:
            raise AppError(404, MESSAGE_CODE.NOT_FOUND, "Employee not found")

        # Check if employee has associated user
        if hasattr(employee, 'user') and employee.user:
            raise AppError(400, MESSAGE_CODE.BAD_REQUEST, "Cannot delete employee with associated user account")

        success = EmployeeRepository.delete(db, employee_id)
        if not success:
            raise AppError(500, MESSAGE_CODE.INTERNAL_ERROR, "Failed to delete employee")
        return {"message": "Employee deleted successfully"}