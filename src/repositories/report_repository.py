# src/repositories/report_repository.py
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from src.models.report_model import Report, ReportStatus

class ReportRepository:
    @staticmethod
    def create(db: Session, report_date: date, name: str, report: str, 
              image_url: Optional[str], status: ReportStatus) -> Report:
        new_report = Report(
            date=report_date,
            name=name,
            report=report,
            image_url=image_url,
            status=status
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        return new_report

    @staticmethod
    def get_by_id(db: Session, report_id: int) -> Optional[Report]:
        return db.query(Report).filter(Report.id == report_id).first()
      
    @staticmethod
    def get_all(db: Session, page: int = 1, per_page: int = 10, search: str = None):
        query = db.query(Report)
        
        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Report.name.ilike(search_filter),
                    Report.report.ilike(search_filter),
                    Report.status.ilike(search_filter)
                )
            )
        
        # Get total count
        total_data = query.count()
        
        # Calculate pagination
        total_pages = (total_data + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Get paginated data
        reports = query.order_by(Report.created_at.desc()).offset(offset).limit(per_page).all()
        
        return {
            "reports": reports,
            "meta": {
                "page": page,
                "perPage": per_page,
                "totalPages": total_pages,
                "totalData": total_data
            }
        }

    # Tambahan method untuk export excel di ReportRepository
    @staticmethod
    def get_all_for_export(db: Session, start_date: Optional[date] = None, end_date: Optional[date] = None):
        query = db.query(Report)
        
        # Apply date filters if provided
        if start_date:
            query = query.filter(Report.date >= start_date)
            
        if end_date:
            query = query.filter(Report.date <= end_date)
        
        # Get all data without pagination for export
        return query.order_by(Report.created_at.desc()).all()

    # @staticmethod
    # def get_all(db: Session, page: int = 1, per_page: int = 10,
    #            status: Optional[str] = None, name: Optional[str] = None,
    #            start_date: Optional[date] = None, end_date: Optional[date] = None):
    #     query = db.query(Report)
        
    #     # Apply filters
    #     if status:
    #         try:
    #             status_enum = ReportStatus(status.lower())
    #             query = query.filter(Report.status == status_enum)
    #         except ValueError:
    #             pass  # Invalid status, ignore filter
        
    #     if name:
    #         search_filter = f"%{name}%"
    #         query = query.filter(Report.name.ilike(search_filter))
        
    #     if start_date:
    #         query = query.filter(Report.date >= start_date)
            
    #     if end_date:
    #         query = query.filter(Report.date <= end_date)
        
    #     # Get total count
    #     total_data = query.count()
        
    #     # Calculate pagination
    #     total_pages = (total_data + per_page - 1) // per_page
    #     offset = (page - 1) * per_page
        
    #     # Get paginated data
    #     reports = query.order_by(Report.created_at.desc()).offset(offset).limit(per_page).all()
        
    #     return {
    #         "reports": reports,
    #         "meta": {
    #             "page": page,
    #             "perPage": per_page,
    #             "totalPages": total_pages,
    #             "totalData": total_data
    #         }
    #     }

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
    def delete(db: Session, report_id: int) -> bool:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            db.delete(report)
            db.commit()
            return True
        return False