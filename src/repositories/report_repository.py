# src/repositories/report_repository.py
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import Optional
from src.models.report_model import Report, ReportStatus
from src.models.employee_model import Employee
from src.models.transaction_model import Transaction
from src.models.customer_model import Customer

class ReportRepository:
    @staticmethod
    def create_pending(
        db: Session, 
        transaction_id: int,
        employee_id: int, 
        description: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        image_url: Optional[str] = None
    ) -> Report:
        new_report = Report(
            transaction_id=transaction_id,
            employee_id=employee_id,
            description=description,
            start_time=start_time,
            end_time=end_time,
            image_url=image_url,
            status=ReportStatus.PENDING
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        return new_report

    @staticmethod
    def get_by_id(db: Session, report_id: int) -> Optional[Report]:
        return db.query(Report).options(
            joinedload(Report.employee),
            joinedload(Report.approver),
            joinedload(Report.user),
            joinedload(Report.transaction).joinedload(Transaction.customer)
        ).filter(Report.id == report_id).first()

    @staticmethod
    def get_all(db: Session, page: int = 1, perPage: int = 10, search: str = None, status: str = None, transaction_id: int = None, karyawan_id: Optional[int] = None):
        query = db.query(Report).options(
            joinedload(Report.employee),
            joinedload(Report.transaction).joinedload(Transaction.customer)
        )
        
        # Filter by employee if not admin
        if karyawan_id:
            query = query.filter(Report.employee_id == karyawan_id)
        
        # Filter by transaction
        if transaction_id:
            query = query.filter(Report.transaction_id == transaction_id)
        
        # Filter by status
        if status:
            try:
                status_enum = ReportStatus(status)
                query = query.filter(Report.status == status_enum)
            except ValueError:
                pass  # Invalid status, ignore filter
        
        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.join(
                Report.employee  # Gunakan relationship yang sudah didefinisikan
            ).join(
                Report.transaction  # Gunakan relationship ke transaction
            ).join(
                Transaction.customer  # Gunakan relationship dari transaction ke customer
            ).filter(
                or_(
                    Employee.name.ilike(search_filter),
                    Report.description.ilike(search_filter),
                    Customer.name.ilike(search_filter),
                    Customer.plate_number.ilike(search_filter)
                )
            )
        
        # Get total count
        total_data = query.count()
        
        # Calculate pagination
        total_pages = (total_data + perPage - 1) // perPage
        offset = (page - 1) * perPage
        
        # Get paginated data
        reports = query.order_by(Report.created_at.desc()).offset(offset).limit(perPage).all()
        
        return {
            "reports": reports,
            "meta": {
                "page": page,
                "perPage": perPage,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }

    @staticmethod
    def get_pending_approval(db: Session, page: int = 1, perPage: int = 10):
        query = db.query(Report).options(
            joinedload(Report.employee),
            joinedload(Report.transaction).joinedload(Transaction.customer)
        ).filter(Report.status == ReportStatus.PENDING)
        
        # Get total count
        total_data = query.count()
        
        # Calculate pagination
        total_pages = (total_data + perPage - 1) // perPage
        offset = (page - 1) * perPage
        
        # Get paginated data
        reports = query.order_by(Report.created_at.asc()).offset(offset).limit(perPage).all()
        
        return {
            "reports": reports,
            "meta": {
                "page": page,
                "perPage": perPage,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }

    @staticmethod
    def get_by_transaction_id(db: Session, transaction_id: int):
        return db.query(Report).options(
            joinedload(Report.employee),
            joinedload(Report.approver),
            joinedload(Report.user),
        ).filter(Report.transaction_id == transaction_id).order_by(Report.created_at.desc()).all()

    @staticmethod
    def get_approved_reports_by_transaction(db: Session, transaction_id: int):
        return db.query(Report).filter(
            and_(
                Report.transaction_id == transaction_id,
                Report.status == ReportStatus.APPROVED
            )
        ).all()

    @staticmethod
    def get_pending_reports_by_transaction(db: Session, transaction_id: int):
        return db.query(Report).filter(
            and_(
                Report.transaction_id == transaction_id,
                Report.status.in_([ReportStatus.PENDING])
            )
        ).all()

    @staticmethod
    def update(db: Session, report_id: int, **kwargs) -> Optional[Report]:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(report, key, value)
            db.commit()
            db.refresh(report)
        return report

    @staticmethod
    def update_status(db: Session, report_id: int, status: ReportStatus) -> Optional[Report]:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = status
            db.commit()
            db.refresh(report)
        return report

    @staticmethod
    def approve(db: Session, report_id: int, approver_id: int, approver_user_id: int) -> Optional[Report]:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = ReportStatus.APPROVED.value
            report.approved_by = approver_id
            report.approved_user_by = approver_user_id
            report.approved_at = datetime.utcnow()
            report.rejection_reason = None
            db.commit()
            db.refresh(report)
        return report

    @staticmethod
    def reject(db: Session, report_id: int, approver_id: int, approver_user_id: int, reason: str) -> Optional[Report]:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = ReportStatus.REJECTED.value
            report.approved_by = approver_id
            report.approved_user_by = approver_user_id
            report.approved_at = datetime.utcnow()
            report.rejection_reason = reason
            db.commit()
            db.refresh(report)
        return report

    @staticmethod
    def delete(db: Session, report_id: int) -> bool:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            db.delete(report)
            db.commit()
            return True
        return False

    @staticmethod
    def get_all_for_export(db: Session, start_date: Optional[str] = None, end_date: Optional[str] = None, status: Optional[str] = None):
        query = db.query(Report).options(
            joinedload(Report.employee),
            joinedload(Report.approver),
            joinedload(Report.user),
            joinedload(Report.transaction).joinedload(Transaction.customer)
        )
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(Report.created_at >= start_date)
        if end_date:
            query = query.filter(Report.created_at <= end_date)
        
        # Apply status filter if provided
        if status:
            try:
                status_enum = ReportStatus(status)
                query = query.filter(Report.status == status_enum)
            except ValueError:
                pass  # Invalid status, ignore filter
        
        return query.order_by(Report.created_at.desc()).all()