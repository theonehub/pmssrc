"""
Employee Salary Application Layer DTOs
Data Transfer Objects for employee salary operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class SalaryComponentTypeEnum(str, Enum):
    """Salary component type enumeration"""
    EARNING = "earning"
    DEDUCTION = "deduction"
    EMPLOYER_CONTRIBUTION = "employer_contribution"


class SalaryFrequencyEnum(str, Enum):
    """Salary frequency enumeration"""
    MONTHLY = "monthly"
    ANNUAL = "annual"
    ONE_TIME = "one_time"


class SalaryStatusEnum(str, Enum):
    """Salary status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# ==================== REQUEST DTOs ====================

class EmployeeSalaryCreateRequestDTO(BaseModel):
    """Request DTO for creating employee salary component"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    component_id: str = Field(..., min_length=1, max_length=50)
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    percentage: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    is_fixed: bool = True
    effective_from: date
    effective_to: Optional[date] = None
    frequency: SalaryFrequencyEnum = SalaryFrequencyEnum.MONTHLY
    is_active: bool = True
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('effective_to')
    def validate_effective_dates(cls, v, values):
        if v and 'effective_from' in values and v <= values['effective_from']:
            raise ValueError("Effective to date must be after effective from date")
        return v
    
    @validator('percentage')
    def validate_percentage_with_fixed(cls, v, values):
        if not values.get('is_fixed', True) and v is None:
            raise ValueError("Percentage is required for non-fixed components")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "component_id": "BASIC_SALARY",
                "amount": 50000.00,
                "is_fixed": True,
                "effective_from": "2024-01-01",
                "frequency": "monthly"
            }
        }


class EmployeeSalaryUpdateRequestDTO(BaseModel):
    """Request DTO for updating employee salary component"""
    amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    percentage: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    is_fixed: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    frequency: Optional[SalaryFrequencyEnum] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('effective_to')
    def validate_effective_dates(cls, v, values):
        if v and 'effective_from' in values and values['effective_from'] and v <= values['effective_from']:
            raise ValueError("Effective to date must be after effective from date")
        return v


class BulkEmployeeSalaryAssignRequestDTO(BaseModel):
    """Request DTO for bulk salary structure assignment"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    components: List[EmployeeSalaryCreateRequestDTO]
    effective_from: date
    replace_existing: bool = False
    
    @validator('components')
    def validate_components(cls, v):
        if not v:
            raise ValueError("At least one component is required")
        
        # Check for duplicate component IDs
        component_ids = [comp.component_id for comp in v]
        if len(set(component_ids)) != len(component_ids):
            raise ValueError("Duplicate component IDs found")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "components": [
                    {
                        "employee_id": "EMP001",
                        "component_id": "BASIC_SALARY",
                        "amount": 50000.00,
                        "is_fixed": True,
                        "effective_from": "2024-01-01"
                    }
                ],
                "effective_from": "2024-01-01",
                "replace_existing": False
            }
        }


class SalaryStructureQueryRequestDTO(BaseModel):
    """Request DTO for salary structure queries"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    as_of_date: Optional[date] = None
    include_inactive: bool = False
    component_type: Optional[SalaryComponentTypeEnum] = None


class SalaryCalculationRequestDTO(BaseModel):
    """Request DTO for salary calculation"""
    employee_id: str = Field(..., min_length=1, max_length=50)
    calculation_date: date
    include_variable_components: bool = True
    override_components: Optional[Dict[str, Decimal]] = None


# ==================== RESPONSE DTOs ====================

class EmployeeSalaryResponseDTO(BaseModel):
    """Response DTO for employee salary component"""
    salary_id: str
    employee_id: str
    component_id: str
    component_name: Optional[str] = None
    component_type: Optional[SalaryComponentTypeEnum] = None
    amount: Decimal
    percentage: Optional[Decimal] = None
    is_fixed: bool
    effective_from: date
    effective_to: Optional[date] = None
    frequency: SalaryFrequencyEnum
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "salary_id": "SAL_001",
                "employee_id": "EMP001",
                "component_id": "BASIC_SALARY",
                "component_name": "Basic Salary",
                "component_type": "earning",
                "amount": 50000.00,
                "is_fixed": True,
                "effective_from": "2024-01-01",
                "frequency": "monthly",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00"
            }
        }


class SalaryStructureResponseDTO(BaseModel):
    """Response DTO for employee salary structure"""
    employee_id: str
    employee_name: Optional[str] = None
    total_earnings: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    components: List[EmployeeSalaryResponseDTO]
    structure_effective_from: date
    last_updated: Optional[datetime] = None
    
    @validator('net_salary')
    def calculate_net_salary(cls, v, values):
        if 'total_earnings' in values and 'total_deductions' in values:
            return values['total_earnings'] - values['total_deductions']
        return v


class SalaryAssignmentStatusResponseDTO(BaseModel):
    """Response DTO for salary assignment status"""
    employee_id: str
    is_assigned: bool
    total_components: int
    active_components: int
    assigned_components: List[EmployeeSalaryResponseDTO]
    last_assignment_date: Optional[datetime] = None


class BulkSalaryAssignmentResponseDTO(BaseModel):
    """Response DTO for bulk salary assignment"""
    employee_id: str
    operation_id: str
    total_components: int
    successful_assignments: int
    failed_assignments: int
    successful_components: List[str]  # Component IDs
    failed_components: List[Dict[str, str]]  # {"component_id": "", "error": ""}
    operation_status: str
    processed_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "operation_id": "BULK_SAL_001",
                "total_components": 5,
                "successful_assignments": 4,
                "failed_assignments": 1,
                "successful_components": ["BASIC_SALARY", "HRA", "DA", "CONVEYANCE"],
                "failed_components": [{"component_id": "INVALID_COMP", "error": "Component not found"}],
                "operation_status": "partially_completed",
                "processed_at": "2024-01-01T12:00:00"
            }
        }


class SalaryCalculationResponseDTO(BaseModel):
    """Response DTO for salary calculation"""
    employee_id: str
    calculation_date: date
    gross_salary: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    earnings_breakdown: Dict[str, Decimal]
    deductions_breakdown: Dict[str, Decimal]
    employer_contributions: Dict[str, Decimal]
    calculated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "calculation_date": "2024-01-31",
                "gross_salary": 75000.00,
                "total_deductions": 15000.00,
                "net_salary": 60000.00,
                "earnings_breakdown": {
                    "BASIC_SALARY": 50000.00,
                    "HRA": 15000.00,
                    "DA": 10000.00
                },
                "deductions_breakdown": {
                    "PF": 6000.00,
                    "ESI": 562.50,
                    "TAX": 8437.50
                },
                "calculated_at": "2024-01-31T23:59:59"
            }
        }


class SalaryHistoryResponseDTO(BaseModel):
    """Response DTO for salary history"""
    employee_id: str
    history_records: List[EmployeeSalaryResponseDTO]
    total_records: int
    date_range: Dict[str, Optional[date]]  # {"from": date, "to": date}
    summary_statistics: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "total_records": 15,
                "date_range": {
                    "from": "2023-01-01",
                    "to": "2024-01-31"
                },
                "summary_statistics": {
                    "average_gross": 72500.00,
                    "salary_increments": 2,
                    "component_changes": 8
                }
            }
        }


class SalaryComponentSummaryResponseDTO(BaseModel):
    """Response DTO for salary component summary"""
    component_id: str
    component_name: str
    component_type: SalaryComponentTypeEnum
    total_employees: int
    average_amount: Decimal
    min_amount: Decimal
    max_amount: Decimal
    frequency_distribution: Dict[str, int]
    active_assignments: int
    inactive_assignments: int


class SalaryAuditResponseDTO(BaseModel):
    """Response DTO for salary audit information"""
    employee_id: str
    audit_records: List[Dict[str, Any]]
    total_changes: int
    last_audit_date: Optional[datetime] = None
    audit_summary: Dict[str, int]


# ==================== ERROR DTOs ====================

class EmployeeSalaryErrorResponseDTO(BaseModel):
    """Response DTO for employee salary errors"""
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    employee_id: Optional[str] = None
    component_id: Optional[str] = None
    salary_id: Optional[str] = None
