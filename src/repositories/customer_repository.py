# src/repositories/customer_repository.py
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from typing import Optional
from src.models.customer_model import Customer
from src.models.transaction_model import Transaction
from src.schemas.customer_schema import CustomerCreateSchema, CustomerUpdateSchema

class CustomerRepository:
    @staticmethod
    def create(db: Session, customer_data: CustomerCreateSchema) -> Customer:
        new_customer = Customer(
            name=customer_data.name,
            address=customer_data.address,
            phone=customer_data.phone,
            email=customer_data.email,
            plate_number=customer_data.plate_number.upper(),
            vehicle_type=customer_data.vehicle_type,
            vehicle_model=customer_data.vehicle_model,
            vehicle_year=customer_data.vehicle_year
        )
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        return new_customer

    @staticmethod
    def get_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def get_by_plate_number(db: Session, plate_number: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.plate_number == plate_number.upper()).first()

    @staticmethod
    def get_all(db: Session, page: int = 1, perPage: int = 10, search: str = None):
        query = db.query(Customer)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Customer.name.ilike(search_filter),
                    Customer.plate_number.ilike(search_filter),
                    Customer.phone.ilike(search_filter),
                    Customer.email.ilike(search_filter),
                    Customer.vehicle_type.ilike(search_filter),
                    Customer.vehicle_model.ilike(search_filter)
                )
            )
        
        # Get total count
        total_data = query.count()
        
        # Calculate pagination
        total_pages = (total_data + perPage - 1) // perPage
        offset = (page - 1) * perPage
        
        # Get paginated data
        customers = query.order_by(Customer.created_at.desc()).offset(offset).limit(perPage).all()
        
        return {
            "customers": customers,
            "meta": {
                "page": page,
                "perPage": perPage,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }

    @staticmethod
    def update(db: Session, customer_id: int, customer_data: CustomerUpdateSchema) -> Optional[Customer]:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            update_data = customer_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(customer, key, value)
            db.commit()
            db.refresh(customer)
        return customer

    @staticmethod
    def delete(db: Session, customer_id: int) -> bool:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            db.delete(customer)
            db.commit()
            return True
        return False

    @staticmethod
    def get_customer_transactions(db: Session, customer_id: int, page: int = 1, perPage: int = 10):
        query = db.query(Transaction).filter(Transaction.customer_id == customer_id)
        
        # Get total count
        total_data = query.count()
        
        # Calculate pagination
        total_pages = (total_data + perPage - 1) // perPage
        offset = (page - 1) * perPage
        
        # Get paginated data
        transactions = query.order_by(Transaction.created_at.desc()).offset(offset).limit(perPage).all()
        
        return {
            "transactions": transactions,
            "meta": {
                "page": page,
                "perPage": perPage,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }