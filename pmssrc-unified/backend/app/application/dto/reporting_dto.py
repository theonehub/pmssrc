"""
Reporting DTOs
Data Transfer Objects for reporting operations
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum

from app.domain.entities.report import Report, ReportType, ReportFormat, ReportStatus


# Custom exceptions for reporting
class ReportingValidationError(Exception):
    """Raised when reporting validation fails."""
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class ReportingBusinessRuleError(Exception):
    """Raised when business rule validation fails."""
    def __init__(self, message: str, rule: str = None):
        super().__init__(message)
        self.rule = rule


class ReportingNotFoundError(Exception):
    """Raised when report is not found."""
    def __init__(self, report_id: str):
        super().__init__(f"Report not found: {report_id}")
        self.report_id = report_id


class ReportingConflictError(Exception):
    """Raised when report operation conflicts with existing data."""
    def __init__(self, message: str, conflict_field: str = None):
        super().__init__(message)
        self.conflict_field = conflict_field


# Request DTOs
@dataclass
class CreateReportRequestDTO:
    """DTO for creating a new report"""
    
    # Required fields
    name: str
    description: str
    report_type: str  # Will be converted to ReportType enum
    format: str = "json"  # Will be converted to ReportFormat enum
    
    # Optional parameters
    parameters: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    # Date range parameters (common for most reports)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    # Filter parameters
    department: Optional[str] = None
    employee_ids: Optional[List[str]] = None
    include_inactive: bool = False
    
    def validate(self) -> List[str]:
        """Validate the request data"""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Name is required")
        
        if not self.description or not self.description.strip():
            errors.append("Description is required")
        
        if not self.report_type:
            errors.append("Report type is required")
        
        # Validate report type
        try:
            ReportType(self.report_type)
        except ValueError:
            valid_types = [rt.value for rt in ReportType]
            errors.append(f"Invalid report type. Valid types: {valid_types}")
        
        # Validate format
        try:
            ReportFormat(self.format)
        except ValueError:
            valid_formats = [rf.value for rf in ReportFormat]
            errors.append(f"Invalid format. Valid formats: {valid_formats}")
        
        # Validate date range if provided
        if self.start_date:
            try:
                datetime.fromisoformat(self.start_date.replace('Z', '+00:00'))
            except ValueError:
                errors.append("Invalid start_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
        
        if self.end_date:
            try:
                datetime.fromisoformat(self.end_date.replace('Z', '+00:00'))
            except ValueError:
                errors.append("Invalid end_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
        
        if self.start_date and self.end_date:
            try:
                start = datetime.fromisoformat(self.start_date.replace('Z', '+00:00'))
                end = datetime.fromisoformat(self.end_date.replace('Z', '+00:00'))
                if start >= end:
                    errors.append("start_date must be before end_date")
            except ValueError:
                pass  # Already handled above
        
        return errors


@dataclass
class UpdateReportRequestDTO:
    """DTO for updating an existing report"""
    
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    
    def validate(self) -> List[str]:
        """Validate the request data"""
        errors = []
        
        if self.name is not None and (not self.name or not self.name.strip()):
            errors.append("Name cannot be empty")
        
        if self.description is not None and (not self.description or not self.description.strip()):
            errors.append("Description cannot be empty")
        
        return errors


@dataclass
class ReportSearchFiltersDTO:
    """DTO for report search filters"""
    
    page: int = 1
    page_size: int = 20
    report_type: Optional[str] = None
    status: Optional[str] = None
    created_by: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    
    def validate(self) -> List[str]:
        """Validate the search filters"""
        errors = []
        
        if self.page < 1:
            errors.append("Page must be >= 1")
        
        if self.page_size < 1 or self.page_size > 1000:
            errors.append("Page size must be between 1 and 1000")
        
        if self.report_type:
            try:
                ReportType(self.report_type)
            except ValueError:
                valid_types = [rt.value for rt in ReportType]
                errors.append(f"Invalid report type. Valid types: {valid_types}")
        
        if self.status:
            try:
                ReportStatus(self.status)
            except ValueError:
                valid_statuses = [rs.value for rs in ReportStatus]
                errors.append(f"Invalid status. Valid statuses: {valid_statuses}")
        
        if self.sort_order not in ["asc", "desc"]:
            errors.append("Sort order must be 'asc' or 'desc'")
        
        return errors


# Response DTOs
@dataclass
class ReportResponseDTO:
    """DTO for report response"""
    
    id: str
    name: str
    description: str
    report_type: str
    format: str
    status: str
    parameters: Dict[str, Any]
    data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_by: Optional[str] = None
    processing_duration: Optional[float] = None
    
    @classmethod
    def from_entity(cls, entity: Report) -> 'ReportResponseDTO':
        """Create DTO from domain entity"""
        return cls(
            id=str(entity.id.value),
            name=entity.name,
            description=entity.description,
            report_type=entity.report_type.value,
            format=entity.format.value,
            status=entity.status.value,
            parameters=entity.parameters,
            data=entity.data,
            file_path=entity.file_path,
            error_message=entity.error_message,
            created_at=entity.created_at.isoformat() if entity.created_at else None,
            updated_at=entity.updated_at.isoformat() if entity.updated_at else None,
            completed_at=entity.completed_at.isoformat() if entity.completed_at else None,
            created_by=entity.created_by,
            processing_duration=entity.get_processing_duration()
        )


@dataclass
class ReportSummaryDTO:
    """DTO for report summary (list view)"""
    
    id: str
    name: str
    report_type: str
    format: str
    status: str
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    processing_duration: Optional[float] = None
    
    @classmethod
    def from_entity(cls, entity: Report) -> 'ReportSummaryDTO':
        """Create summary DTO from domain entity"""
        return cls(
            id=str(entity.id.value),
            name=entity.name,
            report_type=entity.report_type.value,
            format=entity.format.value,
            status=entity.status.value,
            created_at=entity.created_at.isoformat() if entity.created_at else None,
            created_by=entity.created_by,
            processing_duration=entity.get_processing_duration()
        )


@dataclass
class ReportListResponseDTO:
    """DTO for paginated report list response"""
    
    reports: List[ReportSummaryDTO]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


# Analytics DTOs
@dataclass
class DashboardAnalyticsDTO:
    """DTO for dashboard analytics data"""
    
    total_users: int = 0
    active_users: int = 0
    inactive_users: int = 0
    checkin_count: int = 0
    checkout_count: int = 0
    pending_reimbursements: int = 0
    pending_reimbursements_amount: float = 0.0
    approved_reimbursements: int = 0
    approved_reimbursements_amount: float = 0.0
    pending_leaves: int = 0
    total_departments: int = 0
    recent_joiners_count: int = 0
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Additional metrics
    department_distribution: Dict[str, int] = field(default_factory=dict)
    role_distribution: Dict[str, int] = field(default_factory=dict)
    attendance_trends: Dict[str, Any] = field(default_factory=dict)
    leave_trends: Dict[str, Any] = field(default_factory=dict)
    
    # Optional error message for debugging
    error_message: Optional[str] = None


@dataclass
class UserAnalyticsDTO:
    """DTO for user analytics data"""
    
    total_users: int
    active_users: int
    inactive_users: int
    department_distribution: Dict[str, int]
    role_distribution: Dict[str, int]
    recent_joiners: List[Dict[str, Any]]
    user_growth_trends: Dict[str, Any]
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class AttendanceAnalyticsDTO:
    """DTO for attendance analytics data"""
    
    total_checkins_today: int
    total_checkouts_today: int
    present_count: int
    absent_count: int
    late_arrivals: int
    early_departures: int
    average_working_hours: float
    attendance_trends: Dict[str, Any]
    department_attendance: Dict[str, Any]
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class LeaveAnalyticsDTO:
    """DTO for leave analytics data"""
    
    total_pending_leaves: int
    total_approved_leaves: int
    total_rejected_leaves: int
    leave_type_distribution: Dict[str, int]
    department_leave_trends: Dict[str, Any]
    monthly_leave_trends: Dict[str, Any]
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class PayrollAnalyticsDTO:
    """DTO for payroll analytics data"""
    
    total_payouts_current_month: int
    total_amount_current_month: float
    average_salary: float
    department_salary_distribution: Dict[str, Any]
    salary_trends: Dict[str, Any]
    
    # TDS Analytics
    total_tds_current_month: float = 0.0
    average_tds_per_employee: float = 0.0
    tds_trends: Dict[str, Any] = field(default_factory=dict)
    department_tds_distribution: Dict[str, Any] = field(default_factory=dict)
    
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ReimbursementAnalyticsDTO:
    """DTO for reimbursement analytics data"""
    
    total_pending_reimbursements: int
    total_pending_amount: float
    total_approved_reimbursements: int
    total_approved_amount: float
    reimbursement_type_distribution: Dict[str, Any]
    monthly_reimbursement_trends: Dict[str, Any]
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ConsolidatedAnalyticsDTO:
    """DTO for consolidated analytics data"""
    
    dashboard_analytics: DashboardAnalyticsDTO
    user_analytics: UserAnalyticsDTO
    attendance_analytics: AttendanceAnalyticsDTO
    leave_analytics: LeaveAnalyticsDTO
    payroll_analytics: PayrollAnalyticsDTO
    reimbursement_analytics: ReimbursementAnalyticsDTO
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# Export DTOs
@dataclass
class ExportRequestDTO:
    """DTO for export requests"""
    
    report_type: str
    format: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> List[str]:
        """Validate export request"""
        errors = []
        
        if not self.report_type:
            errors.append("Report type is required")
        
        if not self.format:
            errors.append("Format is required")
        
        # Validate report type
        try:
            ReportType(self.report_type)
        except ValueError:
            valid_types = [rt.value for rt in ReportType]
            errors.append(f"Invalid report type. Valid types: {valid_types}")
        
        # Validate format (only file formats for export)
        if self.format not in ["pdf", "excel", "csv"]:
            errors.append("Export format must be one of: pdf, excel, csv")
        
        return errors


@dataclass
class ExportResponseDTO:
    """DTO for export response"""
    
    file_path: str
    file_name: str
    file_size: int
    format: str
    generated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat()) 