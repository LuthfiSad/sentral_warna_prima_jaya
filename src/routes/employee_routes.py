from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session
from src.controllers.employee_controller import EmployeeController
from src.middlewares.catch_wrapper import catch_exceptions
from src.middlewares.admin_middleware import require_admin
from src.config.database import get_db

router = APIRouter()

# @router.get("/")
# @catch_exceptions
# async def get_all_employees(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=1000),
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(require_admin)
# ):
#     return await EmployeeController.get_all_employees(skip, limit, db)

@router.get("/")
@catch_exceptions
async def get_all_employees(
    page: int = Query(1, ge=1),
    perPage: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await EmployeeController.get_all_employees(page, perPage, search, db)

@router.get("/{employee_id}")
@catch_exceptions
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await EmployeeController.get_employee(employee_id, db)

@router.post("/")
@catch_exceptions
async def create_employee(
    name: str = Form(...),
    email: str = Form(...),
    date_of_birth: date = Form(...),
    divisi: str = Form(...),
    address: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await EmployeeController.create_employee(name, email, date_of_birth, divisi, address, image, db)

@router.put("/{employee_id}")
@catch_exceptions
async def update_employee(
    employee_id: int,
    name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    date_of_birth: Optional[date] = Form(None),
    divisi: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await EmployeeController.update_employee(employee_id, name, email, date_of_birth, divisi, address, image, db)

@router.delete("/{employee_id}")
@catch_exceptions
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    return await EmployeeController.delete_employee(employee_id, db)

@router.post("/verify")
@catch_exceptions
async def verify_face_route(
    image: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    return await EmployeeController.verify_face(image, db)