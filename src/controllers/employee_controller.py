from fastapi import Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.services.employee_service import EmployeeService
from src.utils.response import handle_response
from src.utils.message_code import MESSAGE_CODE
from src.config.database import get_db
from datetime import date
from typing import Optional

class EmployeeController:
    @staticmethod
    # async def get_all_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    #     employees = EmployeeService.get_all_employees(db, skip, limit)
    #     return handle_response(200, MESSAGE_CODE.SUCCESS, "Employees retrieved successfully", employees)
    
    @staticmethod
    async def get_all_employees(
        page: int = 1, 
        per_page: int = 10, 
        search: str = None, 
        db: Session = Depends(get_db)
    ):
        result = EmployeeService.get_all_employees(db, page, per_page, search)
        return handle_response(
            200, 
            MESSAGE_CODE.SUCCESS, 
            "Employees retrieved successfully", 
            result["employees"],
            meta=result["meta"]
        )

    @staticmethod
    async def get_employee(employee_id: int, db: Session = Depends(get_db)):
        employee = EmployeeService.get_employee_by_id(db, employee_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Employee retrieved successfully", employee)

    @staticmethod
    async def create_employee(
        name: str = Form(...),
        email: str = Form(...),
        date_of_birth: date = Form(...),
        divisi: str = Form(...),
        address: str = Form(...),
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db)
    ):
        image_data = None
        if image:
            image_data = await image.read()
        
        employee = await EmployeeService.create_employee(
            db, name, email, date_of_birth, divisi, address, image_data
        )
        return handle_response(201, MESSAGE_CODE.CREATED, "Employee created successfully", employee)

    @staticmethod
    async def update_employee(
        employee_id: int,
        name: Optional[str] = Form(None),
        email: Optional[str] = Form(None),
        date_of_birth: Optional[date] = Form(None),
        divisi: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db)
    ):
        image_data = None
        if image:
            image_data = await image.read()
        
        employee = await EmployeeService.update_employee(
            db, employee_id, name, email, date_of_birth, divisi, address, image_data
        )
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Employee updated successfully", employee)

    @staticmethod
    async def delete_employee(employee_id: int, db: Session = Depends(get_db)):
        result = EmployeeService.delete_employee(db, employee_id)
        return handle_response(200, MESSAGE_CODE.SUCCESS, "Employee deleted successfully", result)