# src/repositories/history_repository.py
from sqlalchemy.orm import Session, joinedload
from src.models.history_model import History
from src.models.transaction_model import Transaction, TransactionStatus
from src.models.employee_model import Employee

class HistoryRepository:
    @staticmethod
    def create(
        db: Session, 
        transaction_id: int, 
        status: TransactionStatus, 
        note: str = None,
        created_by: int = None
    ) -> History:
        new_history = History(
            transaction_id=transaction_id,
            status=status,
            note=note,
            created_by=created_by
        )
        db.add(new_history)
        db.commit()
        db.refresh(new_history)
        return new_history

    @staticmethod
    def get_by_transaction_id(db: Session, transaction_id: int):
        return db.query(History).options(
            joinedload(History.transaction).joinedload(Transaction.customer),
            joinedload(History.user)
        ).filter(History.transaction_id == transaction_id).order_by(History.created_at.desc()).all()
        
    @staticmethod
    def get_by_id(db: Session, history_id: int):
        """Get history by ID"""
        from sqlalchemy.orm import joinedload
        return db.query(History).options(
            joinedload(History.transaction)
        ).filter(History.id == history_id).first()

    @staticmethod
    def get_all(db: Session, page: int = 1, perPage: int = 10, transaction_id: int = None, employee_id: int = None):
        """Get all histories with pagination and filtering"""
        from sqlalchemy.orm import joinedload
        
        query = db.query(History).options(
            joinedload(History.transaction).joinedload(Transaction.customer)
        )
        
        # Apply filters
        if transaction_id:
            query = query.filter(History.transaction_id == transaction_id)
        
        if employee_id:
            query = query.filter(History.created_by == employee_id)
        
        # Get total count
        total_data = query.count()
        
        # Calculate pagination
        total_pages = (total_data + perPage - 1) // perPage
        offset = (page - 1) * perPage
        
        # Get paginated data
        histories = query.order_by(History.created_at.desc()).offset(offset).limit(perPage).all()
        
        return {
            "histories": histories,
            "meta": {
                "page": page,
                "perPage": perPage,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }

    @staticmethod
    def get_by_employee_id(db: Session, employee_id: int, page: int = 1, perPage: int = 10):
        """Get histories by employee ID"""
        from sqlalchemy.orm import joinedload
        
        query = db.query(History).options(
            joinedload(History.transaction)
        ).filter(History.created_by == employee_id)
        
        # Get total count
        total_data = query.count()
        
        # Calculate pagination
        total_pages = (total_data + perPage - 1) // perPage
        offset = (page - 1) * perPage
        
        # Get paginated data
        histories = query.order_by(History.created_at.desc()).offset(offset).limit(perPage).all()
        
        return {
            "histories": histories,
            "meta": {
                "page": page,
                "perPage": perPage,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }

    @staticmethod
    def get_recent_activities(db: Session, limit: int = 10):
        """Get recent activities"""
        from sqlalchemy.orm import joinedload
        
        return db.query(History).options(
            joinedload(History.transaction)
        ).order_by(History.created_at.desc()).limit(limit).all()