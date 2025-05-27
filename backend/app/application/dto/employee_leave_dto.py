"""
Employee Leave DTOs
Data Transfer Objects for employee leave operations following SOLID principles
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

from domain.entities.employee_leave import EmployeeLeave
from models.leave_model import LeaveStatus


class EmployeeLeaveCreateRequestDTO(BaseModel):
    """DTO for creating employee leave requests"""
    
    leave_type: str = Field(..., description="Type of leave (e.g., 'CL', 'SL')")
    start_date: str = Field(..., description="Leave start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="Leave end date in YYYY-MM-DD format")
    reason: Optional[str] = Field(None, description="Reason for leave")
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        """Validate date format"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is after start date"""
        if 'start_date' in values:
            start = datetime.strptime(values['start_date'], "%Y-%m-%d")
            end = datetime.strptime(v, "%Y-%m-%d")
            if end < start:
                raise ValueError("End date must be after start date")
        return v
    
    def validate(self) -> List[str]:
        """Validate the request data"""
        errors = []
        
        if not self.leave_type or not self.leave_type.strip():
            errors.append("Leave type is required")
        
        if not self.start_date:
            errors.append("Start date is required")
        
        if not self.end_date:
            errors.append("End date is required")
        
        # Additional business validations can be added here
        
        return errors


class EmployeeLeaveUpdateRequestDTO(BaseModel):
    """DTO for updating employee leave requests"""
    
    leave_type: Optional[str] = Field(None, description="Type of leave")
    start_date: Optional[str] = Field(None, description="Leave start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="Leave end date in YYYY-MM-DD format")
    reason: Optional[str] = Field(None, description="Reason for leave")
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        """Validate date format"""
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%d")
                return v
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class EmployeeLeaveApprovalRequestDTO(BaseModel):
    """DTO for approving/rejecting employee leave requests"""
    
    status: LeaveStatus = Field(..., description="Approval status")
    comments: Optional[str] = Field(None, description="Approval/rejection comments")
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status is either approved or rejected"""
        if v not in [LeaveStatus.APPROVED, LeaveStatus.REJECTED]:
            raise ValueError("Status must be either APPROVED or REJECTED")
        return v


class EmployeeLeaveSearchFiltersDTO(BaseModel):
    """DTO for employee leave search filters"""
    
    employee_id: Optional[str] = Field(None, description="Filter by employee ID")
    manager_id: Optional[str] = Field(None, description="Filter by manager ID")
    leave_type: Optional[str] = Field(None, description="Filter by leave type")
    status: Optional[LeaveStatus] = Field(None, description="Filter by status")
    start_date: Optional[str] = Field(None, description="Filter from start date")
    end_date: Optional[str] = Field(None, description="Filter to end date")
    month: Optional[int] = Field(None, ge=1, le=12, description="Filter by month")
    year: Optional[int] = Field(None, ge=2000, le=3000, description="Filter by year")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")


class EmployeeLeaveResponseDTO(BaseModel):
    """DTO for employee leave response"""
    
    leave_id: str
    employee_id: str
    employee_name: Optional[str] = None
    employee_email: Optional[str] = None
    leave_type: str
    start_date: str
    end_date: str
    leave_count: int
    status: LeaveStatus
    applied_date: str
    approved_by: Optional[str] = None
    approved_date: Optional[str] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_entity(cls, entity: EmployeeLeave) -> 'EmployeeLeaveResponseDTO':
        """Create DTO from domain entity"""
        return cls(
            leave_id=entity.leave_id,
            employee_id=entity.employee_id.value,
            employee_name=entity.employee_name,
            employee_email=entity.employee_email,
            leave_type=entity.leave_type.code,
            start_date=entity.date_range.start_date.strftime("%Y-%m-%d"),
            end_date=entity.date_range.end_date.strftime("%Y-%m-%d"),
            leave_count=entity.working_days_count,
            status=entity.status,
            applied_date=entity.applied_date.strftime("%Y-%m-%d"),
            approved_by=entity.approved_by,
            approved_date=entity.approved_date.strftime("%Y-%m-%d") if entity.approved_date else None,
            reason=entity.reason,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


class EmployeeLeaveBalanceDTO(BaseModel):
    """DTO for employee leave balance"""
    
    employee_id: str
    leave_balances: Dict[str, int] = Field(default_factory=dict, description="Leave type to balance mapping")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


class EmployeeLeaveAnalyticsDTO(BaseModel):
    """DTO for employee leave analytics"""
    
    total_applications: int = 0
    approved_applications: int = 0
    rejected_applications: int = 0
    pending_applications: int = 0
    total_days_taken: int = 0
    leave_type_breakdown: Dict[str, int] = Field(default_factory=dict)
    monthly_breakdown: Dict[str, int] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


class LWPCalculationDTO(BaseModel):
    """DTO for LWP calculation"""
    
    employee_id: str
    month: int
    year: int
    lwp_days: int
    calculation_details: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


# Exception DTOs
class EmployeeLeaveValidationError(Exception):
    """Exception raised when employee leave validation fails"""
    
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}")


class EmployeeLeaveBusinessRuleError(Exception):
    """Exception raised when employee leave business rules are violated"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class EmployeeLeaveNotFoundError(Exception):
    """Exception raised when employee leave is not found"""
    
    def __init__(self, leave_id: str):
        self.leave_id = leave_id
        super().__init__(f"Employee leave not found: {leave_id}")


class InsufficientLeaveBalanceError(Exception):
    """Exception raised when employee has insufficient leave balance"""
    
    def __init__(self, leave_type: str, required: int, available: int):
        self.leave_type = leave_type
        self.required = required
        self.available = available
        super().__init__(f"Insufficient {leave_type} balance. Required: {required}, Available: {available}") 