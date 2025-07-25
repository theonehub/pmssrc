"""
Report Domain Entity
Rich domain entity with behavior for reporting operations
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from app.domain.value_objects.report_id import ReportId


class ReportType(Enum):
    """Report type enumeration"""
    DASHBOARD_ANALYTICS = "dashboard_analytics"
    USER_ANALYTICS = "user_analytics"
    ATTENDANCE_ANALYTICS = "attendance_analytics"
    LEAVE_ANALYTICS = "leave_analytics"
    PAYROLL_ANALYTICS = "payroll_analytics"
    REIMBURSEMENT_ANALYTICS = "reimbursement_analytics"
    CONSOLIDATED_ANALYTICS = "consolidated_analytics"


class ReportFormat(Enum):
    """Report format enumeration"""
    JSON = "json"
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class ReportStatus(Enum):
    """Report status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Report:
    """
    Report domain entity with rich behavior.
    
    Represents a report request and its lifecycle in the system.
    """
    
    id: ReportId
    name: str
    description: str
    report_type: ReportType
    format: ReportFormat
    status: ReportStatus
    parameters: Dict[str, Any]
    data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    @classmethod
    def create(
        cls,
        id: ReportId,
        name: str,
        description: str,
        report_type: ReportType,
        format: ReportFormat,
        parameters: Dict[str, Any],
        created_by: str
    ) -> 'Report':
        """Create a new report."""
        return cls(
            id=id,
            name=name,
            description=description,
            report_type=report_type,
            format=format,
            status=ReportStatus.PENDING,
            parameters=parameters,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    def start_processing(self) -> None:
        """Mark report as processing."""
        if self.status != ReportStatus.PENDING:
            raise ValueError(f"Cannot start processing report in status: {self.status}")
        
        self.status = ReportStatus.PROCESSING
        self.updated_at = datetime.utcnow()
    
    def complete_with_data(self, data: Dict[str, Any], file_path: Optional[str] = None) -> None:
        """Complete report with data."""
        if self.status != ReportStatus.PROCESSING:
            raise ValueError(f"Cannot complete report in status: {self.status}")
        
        self.status = ReportStatus.COMPLETED
        self.data = data
        self.file_path = file_path
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.error_message = None
    
    def fail_with_error(self, error_message: str) -> None:
        """Mark report as failed with error."""
        if self.status not in [ReportStatus.PENDING, ReportStatus.PROCESSING]:
            raise ValueError(f"Cannot fail report in status: {self.status}")
        
        self.status = ReportStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
    
    def update_parameters(self, parameters: Dict[str, Any]) -> None:
        """Update report parameters."""
        if self.status != ReportStatus.PENDING:
            raise ValueError(f"Cannot update parameters for report in status: {self.status}")
        
        self.parameters.update(parameters)
        self.updated_at = datetime.utcnow()
    
    def is_new(self) -> bool:
        """Check if this is a new report (not yet saved)."""
        return self.created_at is None or (datetime.utcnow() - self.created_at).total_seconds() < 1
    
    def is_completed(self) -> bool:
        """Check if report is completed."""
        return self.status == ReportStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if report failed."""
        return self.status == ReportStatus.FAILED
    
    def is_processing(self) -> bool:
        """Check if report is processing."""
        return self.status == ReportStatus.PROCESSING
    
    def get_processing_duration(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if not self.completed_at or not self.created_at:
            return None
        return (self.completed_at - self.created_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return {
            "id": str(self.id.value),
            "name": self.name,
            "description": self.description,
            "report_type": self.report_type.value,
            "format": self.format.value,
            "status": self.status.value,
            "parameters": self.parameters,
            "data": self.data,
            "file_path": self.file_path,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_by": self.created_by
        } 