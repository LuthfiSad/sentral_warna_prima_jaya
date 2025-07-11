# src/repositories/transaction_repository.py
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from src.models.transaction_model import Transaction, TransactionStatus
from src.models.customer_model import Customer
from src.models.report_model import Report
from src.schemas.transaction_schema import TransactionCreateSchema, TransactionUpdateSchema

class TransactionRepository:
    @staticmethod
    def create(db: Session, transaction_data: TransactionCreateSchema) -> Transaction:
        new_transaction = Transaction(
            customer_id=transaction_data.customer_id,
            complaint=transaction_data.complaint,
            status=TransactionStatus.PENDING.value
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return new_transaction

    @staticmethod
    def get_by_id(db: Session, transaction_id: int) -> Optional[Transaction]:
        return db.query(Transaction).options(
            joinedload(Transaction.customer),
            joinedload(Transaction.reports),
            joinedload(Transaction.histories)
        ).filter(Transaction.id == transaction_id).first()

    @staticmethod
    def get_all(db: Session, page: int = 1, perPage: int = 10, search: str = None, status: str = None, karyawan_id: Optional[int] = None):
        query = db.query(Transaction).options(
            joinedload(Transaction.customer),
            joinedload(Transaction.reports)
        )
        
        # Filter by employee if not admin
        if karyawan_id:
            query = query.join(Report).filter(Report.employee_id == karyawan_id)
        
        print(status)
        
        # Apply status filter 
        if status:
            try:
                status_enum = TransactionStatus(status.upper())
                query = query.filter(Transaction.status == status_enum)
            except ValueError:
                pass  # Invalid status, ignore filter
        
        print(query)
        
        # Apply search filter
        if search and search != "selected":
            search_filter = f"%{search}%"
            query = query.join(Customer).filter(
                or_(
                    Customer.name.ilike(search_filter),
                    Customer.plate_number.ilike(search_filter),
                    Transaction.complaint.ilike(search_filter),
                    Customer.vehicle_type.ilike(search_filter)
                )
            )
        
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

    @staticmethod
    def update(db: Session, transaction_id: int, transaction_data: TransactionUpdateSchema) -> Optional[Transaction]:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            update_data = transaction_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(transaction, key, value)
            db.commit()
            db.refresh(transaction)
        return transaction

    @staticmethod
    def update_status(db: Session, transaction_id: int, status: TransactionStatus) -> Optional[Transaction]:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            transaction.status = status
            db.commit()
            db.refresh(transaction)
        return transaction

    @staticmethod
    def update_cost(db: Session, transaction_id: int, total_cost: float) -> Optional[Transaction]:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            transaction.total_cost = total_cost
            db.commit()
            db.refresh(transaction)
        return transaction

    @staticmethod
    def delete(db: Session, transaction_id: int) -> bool:
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            db.delete(transaction)
            db.commit()
            return True
        return False