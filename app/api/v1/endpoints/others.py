from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.repositories.audit_log import AuditLogRepository

router = APIRouter()

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@router.get("/audit-logs")
def get_audit_logs(action: Optional[str] = None, db: Session = Depends(get_db)):
    """Retrieve audit logs."""
    repo = AuditLogRepository(db)
    if action:
        logs = repo.get_by_action(action)
    else:
        logs = repo.get_all()
    
    return {"status": "success", "count": len(logs), "logs": logs}
