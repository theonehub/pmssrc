"""
Employee Leave DTOs
Data Transfer Objects for employee leave operations following SOLID principles
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

from app.domain.entities.employee_leave import EmployeeLeave

# Define LeaveStatus as proper enum for Pydantic
class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    LOW_BALANCE = 'Low balance'
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class EmployeeLeaveCreateRequestDTO(BaseModel):
    """DTO for creating employee leave requests"""
    
    leave_type: Optional[str] = Field(None, description="Type of leave (e.g., 'CL', 'SL')")
    leave_name: Optional[str] = Field(None, description="Frontend field: Type of leave")
    start_date: str = Field(..., description="Leave start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="Leave end date in YYYY-MM-DD format")
    reason: Optional[str] = Field(None, description="Reason for leave")
    employee_id: Optional[str] = Field(None, description="Employee ID (auto-filled from auth)")
    
    def get_leave_type(self) -> str:
        """Get leave type from either field"""
        return self.leave_type or self.leave_name or ""
    
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
        
        leave_type = self.get_leave_type()
        if not leave_type or not leave_type.strip():
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
    leave_name: Optional[str] = Field(None, description="Frontend field: Type of leave")
    start_date: Optional[str] = Field(None, description="Leave start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="Leave end date in YYYY-MM-DD format")
    reason: Optional[str] = Field(None, description="Reason for leave")
    updated_by: Optional[str] = Field(None, description="User updating the leave")
    present_days: Optional[int] = Field(None, description="Present days for LWP calculation")
    is_deleted: Optional[bool] = Field(None, description="Soft delete flag")
    
    def get_leave_type(self) -> Optional[str]:
        """Get leave type from either field"""
        return self.leave_type or self.leave_name
    
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
    
    status: str = Field(..., description="Approval status (approved/rejected)")
    comments: Optional[str] = Field(None, description="Approval/rejection comments")
    approved_by: Optional[str] = Field(None, description="User approving/rejecting the leave")
    
    def get_status(self) -> LeaveStatus:
        """Convert string status to LeaveStatus enum"""
        status_map = {
            "approved": LeaveStatus.APPROVED,
            "rejected": LeaveStatus.REJECTED,
            "pending": LeaveStatus.PENDING,
            "cancelled": LeaveStatus.CANCELLED
        }
        return status_map.get(self.status.lower(), LeaveStatus.PENDING)
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status is either approved or rejected"""
        valid_statuses = ["approved", "rejected", "pending", "cancelled"]
        if v.lower() not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v.lower()


class EmployeeLeaveSearchFiltersDTO(BaseModel):
    """DTO for employee leave search filters"""
    
    employee_id: Optional[str] = Field(None, description="Filter by employee ID")
    manager_id: Optional[str] = Field(None, description="Filter by manager ID")
    employee_name: Optional[str] = Field(None, description="Filter by employee name")
    leave_type: Optional[str] = Field(None, description="Filter by leave type")
    status: Optional[str] = Field(None, description="Filter by status")
    start_date: Optional[str] = Field(None, description="Filter from start date")
    end_date: Optional[str] = Field(None, description="Filter to end date")
    month: Optional[int] = Field(None, ge=1, le=12, description="Filter by month")
    year: Optional[int] = Field(None, ge=2000, le=3000, description="Filter by year")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")
    page: Optional[int] = Field(1, ge=1, description="Page number")
    page_size: Optional[int] = Field(100, ge=1, le=1000, description="Page size")
    search_term: Optional[str] = Field(None, description="General search term for text search")
    include_deleted: bool = Field(False, description="Whether to include soft-deleted records")
    sort_by: Optional[str] = Field("created_at", description="Field to sort by")
    sort_desc: bool = Field(True, description="Whether to sort in descending order")
    
    def get_status_enum(self) -> Optional[LeaveStatus]:
        """Convert string status to LeaveStatus enum"""
        if not self.status:
            return None
        status_map = {
            "approved": LeaveStatus.APPROVED,
            "rejected": LeaveStatus.REJECTED,
            "pending": LeaveStatus.PENDING,
            "cancelled": LeaveStatus.CANCELLED
        }
        return status_map.get(self.status.lower())


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
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_entity(cls, entity: EmployeeLeave) -> 'EmployeeLeaveResponseDTO':
        """Create DTO from app.domain entity"""
        return cls(
            leave_id=entity.leave_id,
            employee_id=entity.employee_id,
            employee_name=getattr(entity, 'employee_name', ''),
            employee_email=getattr(entity, 'employee_email', ''),
            leave_type=entity.leave_name,  # Use leave_name for leave type
            start_date=entity.start_date.strftime("%Y-%m-%d"),
            end_date=entity.end_date.strftime("%Y-%m-%d"),
            leave_count=entity.applied_days,
            status=entity.status,
            applied_date=entity.applied_at.strftime("%Y-%m-%d"),
            approved_by=entity.approved_by,
            approved_date=entity.approved_at.strftime("%Y-%m-%d") if entity.approved_at else None,
            reason=entity.reason,
            created_at=entity.created_at.strftime("%Y-%m-%d %H:%M:%S") if entity.created_at else None,
            updated_at=entity.updated_at.strftime("%Y-%m-%d %H:%M:%S") if entity.updated_at else None
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.dict()


class EmployeeLeaveBalanceDTO(BaseModel):
    """DTO for employee leave balance"""
    
    employee_id: str
    balances: Dict[str, float] = Field(default_factory=dict, description="Leave type to balance mapping")
    leave_balances: Dict[str, float] = Field(default_factory=dict, description="Backward compatibility field")
    
    @validator('balances', 'leave_balances', pre=True)
    def validate_balance_values(cls, v):
        """Validate and convert balance values to ensure they are floats"""
        if not isinstance(v, dict):
            return {}
        
        validated_dict = {}
        for leave_type, balance in v.items():
            try:
                if balance is None:
                    validated_dict[leave_type] = 0.0
                elif isinstance(balance, (int, float)):
                    validated_dict[leave_type] = max(0.0, float(balance))
                elif isinstance(balance, str):
                    validated_dict[leave_type] = max(0.0, float(balance))
                else:
                    validated_dict[leave_type] = 0.0
            except (ValueError, TypeError):
                validated_dict[leave_type] = 0.0
        
        return validated_dict
    
    def __init__(self, **data):
        super().__init__(**data)
        # Ensure both fields are populated for compatibility
        if self.balances and not self.leave_balances:
            self.leave_balances = self.balances
        elif self.leave_balances and not self.balances:
            self.balances = self.leave_balances
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary - return just the balances for frontend"""
        return self.balances or self.leave_balances or {}


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
    working_days: int = Field(default=22, description="Working days in the month")
    lwp_amount: float = Field(default=0.0, description="LWP amount deduction")
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