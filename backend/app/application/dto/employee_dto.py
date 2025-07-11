"""
Employee Data Transfer Objects
DTOs for employee-related operations
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal


@dataclass
class CreateEmployeeRequest:
    """
    Request DTO for creating a new employee.
    
    Follows SOLID principles:
    - SRP: Only handles employee creation request data
    - OCP: Can be extended with new fields without breaking existing code
    - LSP: Can be substituted with other request DTOs
    - ISP: Contains only fields needed for employee creation
    - DIP: Doesn't depend on concrete implementations
    """
    
    # Required fields
    employee_id: str
    first_name: str
    last_name: str
    email: str
    date_of_joining: date
    date_of_birth: date
    date_of_leaving: Optional[date] = None
    
    # Optional fields
    phone: Optional[str] = None
    initial_salary: Optional[float] = None
    employee_type: Optional[str] = None  # permanent, contract, temporary, intern, consultant
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_id: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    emergency_contact: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """Validate and clean data after initialization"""
        # Clean string fields
        if self.employee_id:
            self.employee_id = self.employee_id.strip().upper()
        
        if self.first_name:
            self.first_name = self.first_name.strip()
        
        if self.last_name:
            self.last_name = self.last_name.strip()
        
        if self.email:
            self.email = self.email.strip().lower()
        
        if self.phone:
            self.phone = self.phone.strip()
        
        if self.employee_type:
            self.employee_type = self.employee_type.strip().lower()
        
        if self.department:
            self.department = self.department.strip()
        
        if self.designation:
            self.designation = self.designation.strip()
        
        if self.manager_id:
            self.manager_id = self.manager_id.strip().upper()


@dataclass
class CreateEmployeeResponse:
    """
    Response DTO for employee creation.
    
    Contains the essential information about the created employee.
    """
    
    employee_id: str
    full_name: str
    email: str
    department: Optional[str]
    designation: Optional[str]
    date_of_joining: date
    date_of_leaving: Optional[date] = None
    employee_type: str
    status: str
    current_salary: float
    created_at: datetime


@dataclass
class UpdateEmployeeRequest:
    """
    Request DTO for updating employee information.
    
    All fields are optional to support partial updates.
    """
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_id: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    emergency_contact: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """Clean data after initialization"""
        if self.first_name:
            self.first_name = self.first_name.strip()
        
        if self.last_name:
            self.last_name = self.last_name.strip()
        
        if self.email:
            self.email = self.email.strip().lower()
        
        if self.phone:
            self.phone = self.phone.strip()
        
        if self.department:
            self.department = self.department.strip()
        
        if self.designation:
            self.designation = self.designation.strip()
        
        if self.manager_id:
            self.manager_id = self.manager_id.strip().upper()


@dataclass
class ChangeSalaryRequest:
    """Request DTO for changing employee salary"""
    
    employee_id: str
    new_salary: float
    effective_date: date
    reason: str
    changed_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate and clean data"""
        if self.employee_id:
            self.employee_id = self.employee_id.strip().upper()
        
        if self.reason:
            self.reason = self.reason.strip()
        
        if self.changed_by:
            self.changed_by = self.changed_by.strip().upper()
        
        if self.new_salary <= 0:
            raise ValueError("New salary must be positive")


@dataclass
class PromoteEmployeeRequest:
    """Request DTO for promoting an employee"""
    
    employee_id: str
    new_designation: str
    new_salary: float
    effective_date: date
    promoted_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate and clean data"""
        if self.employee_id:
            self.employee_id = self.employee_id.strip().upper()
        
        if self.new_designation:
            self.new_designation = self.new_designation.strip()
        
        if self.promoted_by:
            self.promoted_by = self.promoted_by.strip().upper()
        
        if self.new_salary <= 0:
            raise ValueError("New salary must be positive")


@dataclass
class EmployeeResponse:
    """
    Response DTO for employee information.
    
    Contains comprehensive employee data for API responses.
    """
    
    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone: Optional[str]
    date_of_joining: date
    date_of_birth: date
    date_of_leaving: Optional[date] = None
    age: int
    years_of_service: int
    employee_type: str
    status: str
    department: Optional[str]
    designation: Optional[str]
    location: Optional[str]
    manager_id: Optional[str]
    current_salary: float
    address: Optional[Dict[str, str]]
    emergency_contact: Optional[Dict[str, str]]
    is_senior_citizen: bool
    is_super_senior_citizen: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class EmployeeListResponse:
    """Response DTO for employee list operations"""
    
    employees: List[EmployeeResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


@dataclass
class EmployeeSearchRequest:
    """Request DTO for searching employees"""
    
    name_pattern: Optional[str] = None
    email_pattern: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    employee_type: Optional[str] = None
    status: Optional[str] = None
    manager_id: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    joining_date_from: Optional[date] = None
    joining_date_to: Optional[date] = None
    page: int = 1
    page_size: int = 20
    
    def __post_init__(self):
        """Validate and clean search parameters"""
        if self.name_pattern:
            self.name_pattern = self.name_pattern.strip()
        
        if self.email_pattern:
            self.email_pattern = self.email_pattern.strip().lower()
        
        if self.department:
            self.department = self.department.strip()
        
        if self.designation:
            self.designation = self.designation.strip()
        
        if self.employee_type:
            self.employee_type = self.employee_type.strip().lower()
        
        if self.status:
            self.status = self.status.strip().lower()
        
        if self.manager_id:
            self.manager_id = self.manager_id.strip().upper()
        
        if self.page < 1:
            self.page = 1
        
        if self.page_size < 1:
            self.page_size = 20
        elif self.page_size > 100:
            self.page_size = 100
        
        if self.min_salary and self.min_salary < 0:
            self.min_salary = 0
        
        if self.max_salary and self.max_salary < 0:
            self.max_salary = None
        
        if (self.min_salary and self.max_salary and 
            self.min_salary > self.max_salary):
            raise ValueError("Minimum salary cannot be greater than maximum salary")
        
        if (self.joining_date_from and self.joining_date_to and 
            self.joining_date_from > self.joining_date_to):
            raise ValueError("Joining date from cannot be after joining date to")


@dataclass
class EmployeeStatisticsResponse:
    """Response DTO for employee statistics"""
    
    total_employees: int
    active_employees: int
    inactive_employees: int
    terminated_employees: int
    department_wise_count: Dict[str, int]
    employee_type_wise_count: Dict[str, int]
    average_salary: float
    median_salary: float
    salary_range: Dict[str, float]  # min, max
    average_age: float
    average_tenure: float
    senior_citizens_count: int
    super_senior_citizens_count: int


@dataclass
class ActivateEmployeeRequest:
    """Request DTO for activating an employee"""
    
    employee_id: str
    activated_by: Optional[str] = None
    
    def __post_init__(self):
        if self.employee_id:
            self.employee_id = self.employee_id.strip().upper()
        
        if self.activated_by:
            self.activated_by = self.activated_by.strip().upper()


@dataclass
class DeactivateEmployeeRequest:
    """Request DTO for deactivating an employee"""
    
    employee_id: str
    reason: str
    deactivated_by: Optional[str] = None
    
    def __post_init__(self):
        if self.employee_id:
            self.employee_id = self.employee_id.strip().upper()
        
        if self.reason:
            self.reason = self.reason.strip()
        
        if self.deactivated_by:
            self.deactivated_by = self.deactivated_by.strip().upper()
        
        if not self.reason:
            raise ValueError("Deactivation reason is required")


@dataclass
class TerminateEmployeeRequest:
    """Request DTO for terminating an employee"""
    
    employee_id: str
    termination_date: date
    reason: str
    terminated_by: Optional[str] = None
    
    def __post_init__(self):
        if self.employee_id:
            self.employee_id = self.employee_id.strip().upper()
        
        if self.reason:
            self.reason = self.reason.strip()
        
        if self.terminated_by:
            self.terminated_by = self.terminated_by.strip().upper()
        
        if not self.reason:
            raise ValueError("Termination reason is required")


@dataclass
class TransferEmployeeRequest:
    """Request DTO for transferring an employee to a new department"""
    
    employee_id: str
    new_department: str
    effective_date: date
    transferred_by: Optional[str] = None
    
    def __post_init__(self):
        if self.employee_id:
            self.employee_id = self.employee_id.strip().upper()
        
        if self.new_department:
            self.new_department = self.new_department.strip()
        
        if self.transferred_by:
            self.transferred_by = self.transferred_by.strip().upper()
        
        if not self.new_department:
            raise ValueError("New department is required")


# Response status codes for better API responses
@dataclass
class EmployeeOperationResponse:
    """Generic response for employee operations"""
    
    success: bool
    message: str
    employee_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None 