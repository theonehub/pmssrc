"""
Attendance DTOs (Data Transfer Objects)
Handles data transfer between layers and API validation
"""

from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, validator, model_validator
from enum import Enum


# ==================== ENUMS ====================

class AttendanceStatusEnum(str, Enum):
    """Attendance status enumeration for API"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    WORK_FROM_HOME = "work_from_home"
    ON_LEAVE = "on_leave"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"


class AttendanceMarkingTypeEnum(str, Enum):
    """Attendance marking type enumeration for API"""
    MANUAL = "manual"
    BIOMETRIC = "biometric"
    MOBILE_APP = "mobile_app"
    WEB_APP = "web_app"
    SYSTEM_AUTO = "system_auto"
    ADMIN_OVERRIDE = "admin_override"


# ==================== REQUEST DTOs ====================

class AttendanceCheckInRequestDTO(BaseModel):
    """DTO for check-in requests"""
    employee_id: Optional[str] = Field(None, description="Employee ID")
    emp_id: Optional[str] = Field(None, description="Employee ID (alternate field name)")
    check_in_time: Optional[datetime] = Field(None, description="Check-in time (defaults to current time)")
    timestamp: Optional[datetime] = Field(None, description="Timestamp (alternate field name)")
    location: Optional[str] = Field(None, description="Check-in location")
    hostname: Optional[str] = Field(None, description="Hostname")
    
    @model_validator(mode='after')
    def validate_employee_required(self):
        """Final validation to ensure either employee_id or emp_id is provided"""
        # Use emp_id if employee_id is not provided
        if not self.employee_id and self.emp_id:
            self.employee_id = str(self.emp_id).strip()
        
        if not self.employee_id or not str(self.employee_id).strip():
            raise ValueError("Employee ID is required")
            
        # Use timestamp if check_in_time is not provided
        if not self.check_in_time and self.timestamp:
            self.check_in_time = self.timestamp
            
        if self.check_in_time and self.check_in_time > datetime.now():
            raise ValueError("Check-in time cannot be in the future")
            
        return self


class AttendanceCheckOutRequestDTO(BaseModel):
    """DTO for check-out requests"""
    employee_id: Optional[str] = Field(None, description="Employee ID")
    emp_id: Optional[str] = Field(None, description="Employee ID (alternate field name)")
    check_out_time: Optional[datetime] = Field(None, description="Check-out time (defaults to current time)")
    timestamp: Optional[datetime] = Field(None, description="Timestamp (alternate field name)")
    location: Optional[str] = Field(None, description="Check-out location")
    hostname: Optional[str] = Field(None, description="Hostname")
    
    @model_validator(mode='after')
    def validate_employee_required(self):
        """Final validation to ensure either employee_id or emp_id is provided"""
        # Use emp_id if employee_id is not provided
        if not self.employee_id and self.emp_id:
            self.employee_id = str(self.emp_id).strip()
        
        if not self.employee_id or not str(self.employee_id).strip():
            raise ValueError("Employee ID is required")
            
        # Use timestamp if check_out_time is not provided
        if not self.check_out_time and self.timestamp:
            self.check_out_time = self.timestamp
            
        if self.check_out_time and self.check_out_time > datetime.now():
            raise ValueError("Check-out time cannot be in the future")
            
        return self


class AttendanceBreakRequestDTO(BaseModel):
    """DTO for break start/end requests"""
    employee_id: Optional[str] = Field(None, description="Employee ID")
    emp_id: Optional[str] = Field(None, description="Employee ID (alternate field name)")
    break_time: Optional[datetime] = Field(None, description="Break time (defaults to current time)")
    timestamp: Optional[datetime] = Field(None, description="Timestamp (alternate field name)")
    break_type: str = Field("start", description="Break type: 'start' or 'end'")
    hostname: Optional[str] = Field(None, description="Hostname")
    
    @model_validator(mode='after')
    def validate_employee_required(self):
        """Final validation to ensure either employee_id or emp_id is provided"""
        # Use emp_id if employee_id is not provided
        if not self.employee_id and self.emp_id:
            self.employee_id = str(self.emp_id).strip()
        
        if not self.employee_id or not str(self.employee_id).strip():
            raise ValueError("Employee ID is required")
            
        # Use timestamp if break_time is not provided
        if not self.break_time and self.timestamp:
            self.break_time = self.timestamp
            
        if self.break_type not in ["start", "end"]:
            raise ValueError("Break type must be 'start' or 'end'")
            
        return self


class AttendanceRegularizationRequestDTO(BaseModel):
    """DTO for attendance regularization requests"""
    attendance_id: str = Field(..., description="Attendance ID")
    reason: str = Field(..., description="Regularization reason")
    new_status: Optional[AttendanceStatusEnum] = Field(None, description="New status (optional)")
    
    @validator('reason')
    def validate_reason(cls, v):
        if not v or not v.strip():
            raise ValueError("Regularization reason is required")
        if len(v.strip()) < 10:
            raise ValueError("Regularization reason must be at least 10 characters")
        return v.strip()


class AttendanceUpdateRequestDTO(BaseModel):
    """DTO for attendance update requests"""
    attendance_id: str = Field(..., description="Attendance ID")
    new_status: AttendanceStatusEnum = Field(..., description="New attendance status")
    reason: Optional[str] = Field(None, description="Update reason")
    check_in_time: Optional[datetime] = Field(None, description="Updated check-in time")
    check_out_time: Optional[datetime] = Field(None, description="Updated check-out time")
    
    @validator('reason')
    def validate_reason(cls, v):
        if v and len(v.strip()) < 5:
            raise ValueError("Update reason must be at least 5 characters")
        return v.strip() if v else None


class AttendanceBulkUpdateRequestDTO(BaseModel):
    """DTO for bulk attendance updates"""
    attendance_ids: List[str] = Field(..., description="List of attendance IDs")
    new_status: AttendanceStatusEnum = Field(..., description="New status for all records")
    reason: str = Field(..., description="Bulk update reason")
    
    @validator('attendance_ids')
    def validate_attendance_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one attendance ID is required")
        if len(v) > 100:
            raise ValueError("Cannot update more than 100 records at once")
        return v
    
    @validator('reason')
    def validate_reason(cls, v):
        if not v or not v.strip():
            raise ValueError("Bulk update reason is required")
        return v.strip()


class AttendanceCommentRequestDTO(BaseModel):
    """DTO for adding comments to attendance"""
    attendance_id: str = Field(..., description="Attendance ID")
    comment: str = Field(..., description="Comment text")
    
    @validator('comment')
    def validate_comment(cls, v):
        if not v or not v.strip():
            raise ValueError("Comment is required")
        if len(v.strip()) > 500:
            raise ValueError("Comment cannot exceed 500 characters")
        return v.strip()


# ==================== SEARCH AND FILTER DTOs ====================

class AttendanceSearchFiltersDTO(BaseModel):
    """DTO for attendance search filters"""
    employee_id: Optional[str] = Field(None, description="Filter by employee ID")
    emp_id: Optional[str] = Field(None, description="Filter by employee ID (alternate field name)")
    employee_ids: Optional[List[str]] = Field(None, description="Filter by multiple employee IDs")
    manager_id: Optional[str] = Field(None, description="Filter by manager ID for team queries")
    status: Optional[AttendanceStatusEnum] = Field(None, description="Filter by status")
    statuses: Optional[List[AttendanceStatusEnum]] = Field(None, description="Filter by multiple statuses")
    start_date: Optional[date] = Field(None, description="Start date filter")
    end_date: Optional[date] = Field(None, description="End date filter")
    date: Optional[int] = Field(None, ge=1, le=31, description="Specific date (1-31)")
    month: Optional[int] = Field(None, ge=1, le=12, description="Specific month (1-12)")
    year: Optional[int] = Field(None, ge=2000, le=3000, description="Specific year")
    hostname: Optional[str] = Field(None, description="Filter by hostname")
    is_regularized: Optional[bool] = Field(None, description="Filter by regularization status")
    has_overtime: Optional[bool] = Field(None, description="Filter by overtime presence")
    marking_type: Optional[AttendanceMarkingTypeEnum] = Field(None, description="Filter by marking type")
    location: Optional[str] = Field(None, description="Filter by location")
    limit: Optional[int] = Field(100, description="Maximum number of results")
    offset: Optional[int] = Field(0, description="Offset for pagination")
    
    @validator('limit')
    def validate_limit(cls, v):
        if v and (v < 1 or v > 1000):
            raise ValueError("Limit must be between 1 and 1000")
        return v
    
    @validator('offset')
    def validate_offset(cls, v):
        if v and v < 0:
            raise ValueError("Offset cannot be negative")
        return v
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError("End date must be after start date")
        return v


# ==================== RESPONSE DTOs ====================

class WorkingHoursResponseDTO(BaseModel):
    """DTO for working hours response"""
    check_in_time: Optional[datetime] = Field(None, description="Check-in time")
    check_out_time: Optional[datetime] = Field(None, description="Check-out time")
    total_hours: float = Field(0.0, description="Total working hours")
    break_hours: float = Field(0.0, description="Total break hours")
    overtime_hours: float = Field(0.0, description="Overtime hours")
    shortage_hours: float = Field(0.0, description="Shortage hours")
    expected_hours: float = Field(8.0, description="Expected working hours")
    is_complete_day: bool = Field(False, description="Whether it's a complete day")
    is_full_day: bool = Field(False, description="Whether it qualifies as full day")
    is_half_day: bool = Field(False, description="Whether it qualifies as half day")


class AttendanceStatusResponseDTO(BaseModel):
    """DTO for attendance status response"""
    status: AttendanceStatusEnum = Field(..., description="Attendance status")
    marking_type: AttendanceMarkingTypeEnum = Field(..., description="How attendance was marked")
    is_regularized: bool = Field(False, description="Whether attendance is regularized")
    regularization_reason: Optional[str] = Field(None, description="Regularization reason")


class AttendanceResponseDTO(BaseModel):
    """DTO for attendance response"""
    attendance_id: str = Field(..., description="Attendance ID")
    employee_id: str = Field(..., description="Employee ID")
    attendance_date: date = Field(..., description="Attendance date")
    status: AttendanceStatusResponseDTO = Field(..., description="Attendance status")
    working_hours: WorkingHoursResponseDTO = Field(..., description="Working hours details")
    check_in_location: Optional[str] = Field(None, description="Check-in location")
    check_out_location: Optional[str] = Field(None, description="Check-out location")
    comments: Optional[str] = Field(None, description="Comments")
    admin_notes: Optional[str] = Field(None, description="Admin notes")
    created_at: datetime = Field(..., description="Created timestamp")
    created_by: str = Field(..., description="Created by")
    updated_at: Optional[datetime] = Field(None, description="Updated timestamp")
    updated_by: Optional[str] = Field(None, description="Updated by")


class AttendanceSummaryDTO(BaseModel):
    """DTO for attendance summary"""
    employee_id: str = Field(..., description="Employee ID")
    total_days: int = Field(0, description="Total days in period")
    present_days: int = Field(0, description="Present days")
    absent_days: int = Field(0, description="Absent days")
    late_days: int = Field(0, description="Late arrival days")
    half_days: int = Field(0, description="Half days")
    work_from_home_days: int = Field(0, description="Work from home days")
    leave_days: int = Field(0, description="Leave days")
    holiday_days: int = Field(0, description="Holiday days")
    total_working_hours: float = Field(0.0, description="Total working hours")
    total_overtime_hours: float = Field(0.0, description="Total overtime hours")
    average_working_hours: float = Field(0.0, description="Average working hours per day")
    attendance_percentage: float = Field(0.0, description="Attendance percentage")


# ==================== STATISTICS DTOs ====================

class AttendanceStatisticsDTO(BaseModel):
    """DTO for attendance statistics"""
    total_employees: int = Field(0, description="Total employees")
    present_today: int = Field(0, description="Present today")
    absent_today: int = Field(0, description="Absent today")
    late_today: int = Field(0, description="Late today")
    on_leave_today: int = Field(0, description="On leave today")
    work_from_home_today: int = Field(0, description="Work from home today")
    checked_in: int = Field(0, description="Checked in")
    checked_out: int = Field(0, description="Checked out")
    pending_check_out: int = Field(0, description="Pending check out")
    average_working_hours: float = Field(0.0, description="Average working hours")
    total_overtime_hours: float = Field(0.0, description="Total overtime hours")
    attendance_percentage: float = Field(0.0, description="Overall attendance percentage")


class DepartmentAttendanceDTO(BaseModel):
    """DTO for department-wise attendance"""
    department_id: str = Field(..., description="Department ID")
    department_name: str = Field(..., description="Department name")
    total_employees: int = Field(0, description="Total employees in department")
    present_count: int = Field(0, description="Present count")
    absent_count: int = Field(0, description="Absent count")
    attendance_percentage: float = Field(0.0, description="Department attendance percentage")


class AttendanceTrendDTO(BaseModel):
    """DTO for attendance trends"""
    trend_date: date = Field(..., description="Date")
    total_employees: int = Field(0, description="Total employees")
    present_count: int = Field(0, description="Present count")
    absent_count: int = Field(0, description="Absent count")
    late_count: int = Field(0, description="Late count")
    attendance_percentage: float = Field(0.0, description="Attendance percentage")
    average_working_hours: float = Field(0.0, description="Average working hours")


# ==================== REPORT DTOs ====================

class AttendanceReportRequestDTO(BaseModel):
    """DTO for attendance report requests"""
    report_type: str = Field(..., description="Report type: 'daily', 'weekly', 'monthly', 'custom'")
    start_date: date = Field(..., description="Report start date")
    end_date: date = Field(..., description="Report end date")
    employee_ids: Optional[List[str]] = Field(None, description="Specific employee IDs (optional)")
    department_ids: Optional[List[str]] = Field(None, description="Specific department IDs (optional)")
    include_summary: bool = Field(True, description="Include summary statistics")
    include_details: bool = Field(True, description="Include detailed records")
    format: str = Field("json", description="Report format: 'json', 'csv', 'excel'")
    
    @validator('report_type')
    def validate_report_type(cls, v):
        if v not in ["daily", "weekly", "monthly", "custom"]:
            raise ValueError("Invalid report type")
        return v
    
    @validator('format')
    def validate_format(cls, v):
        if v not in ["json", "csv", "excel"]:
            raise ValueError("Invalid report format")
        return v
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError("End date must be after start date")
        return v


class AttendanceReportResponseDTO(BaseModel):
    """DTO for attendance report response"""
    report_id: str = Field(..., description="Report ID")
    report_type: str = Field(..., description="Report type")
    period_start: date = Field(..., description="Report period start")
    period_end: date = Field(..., description="Report period end")
    generated_at: datetime = Field(..., description="Report generation time")
    generated_by: str = Field(..., description="Report generated by")
    summary: AttendanceStatisticsDTO = Field(..., description="Report summary")
    records: List[AttendanceResponseDTO] = Field([], description="Detailed records")
    download_url: Optional[str] = Field(None, description="Download URL for file formats")


# ==================== EXCEPTION DTOs ====================

class AttendanceValidationError(Exception):
    """Custom exception for attendance validation errors"""
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AttendanceBusinessRuleError(Exception):
    """Custom exception for attendance business rule violations"""
    def __init__(self, message: str, error_code: str = "BUSINESS_RULE_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class AttendanceNotFoundError(Exception):
    """Custom exception for attendance not found errors"""
    def __init__(self, message: str = "Attendance record not found", error_code: str = "NOT_FOUND"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


# ==================== UTILITY DTOs ====================

class AttendanceHealthCheckDTO(BaseModel):
    """DTO for attendance system health check"""
    status: str = Field("healthy", description="System status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Health check timestamp")
    database_status: str = Field("connected", description="Database connection status")
    total_records: int = Field(0, description="Total attendance records")
    today_records: int = Field(0, description="Today's attendance records")


class AttendanceBulkImportDTO(BaseModel):
    """DTO for bulk attendance import"""
    records: List[Dict[str, Any]] = Field(..., description="Attendance records to import")
    import_mode: str = Field("create", description="Import mode: 'create', 'update', 'upsert'")
    validate_only: bool = Field(False, description="Only validate without importing")
    
    @validator('import_mode')
    def validate_import_mode(cls, v):
        if v not in ["create", "update", "upsert"]:
            raise ValueError("Invalid import mode")
        return v
    
    @validator('records')
    def validate_records(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one record is required")
        if len(v) > 1000:
            raise ValueError("Cannot import more than 1000 records at once")
        return v


class AttendanceBulkImportResultDTO(BaseModel):
    """DTO for bulk import results"""
    total_records: int = Field(0, description="Total records processed")
    successful_imports: int = Field(0, description="Successful imports")
    failed_imports: int = Field(0, description="Failed imports")
    validation_errors: List[str] = Field([], description="Validation errors")
    import_summary: Dict[str, Any] = Field({}, description="Import summary")
    imported_ids: List[str] = Field([], description="Successfully imported attendance IDs") 