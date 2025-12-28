from typing import List
from sqlalchemy import desc
from .base import BaseRepository
from app.models.models import AuditLog

class AuditLogRepository(BaseRepository):
    """Repository for Audit Log operations"""

    def get_by_action(self, action: str) -> List[AuditLog]:
        """Get audit logs by action"""
        return self.db.query(AuditLog).filter(
            AuditLog.action == action
        ).order_by(desc(AuditLog.created_at)).all()

    def get_all(self) -> List[AuditLog]:
        """Get all audit logs"""
        return self.db.query(AuditLog).order_by(desc(AuditLog.created_at)).all()
