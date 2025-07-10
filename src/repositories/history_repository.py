# src/repositories/history_repository.py
from sqlalchemy.orm import Session, joinedload
from src.models.history_model import History
from src.models.transaction_model import TransactionStatus
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
            joinedload(History.employee)
        ).filter(History.transaction_id == transaction_id).order_by(History.created_at.desc()).all()