"""
Company Leave Data Transfer Objects
DTOs for company leave-related operations
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

@dataclass
class CreateCompanyLeaveRequestDTO:
    """
    DTO for company leave creation request.
    
    Follows SOLID principles:
    - SRP: Only handles company leave creation request data
    - OCP: Can be extended with new fields without breaking existing code
    - LSP: Can be substituted with other request DTOs
    - ISP: Contains only company leave creation related fields
    - DIP: Doesn't depend on concrete implementations
    """
    
    leave_name: str
    accrual_type: str
    annual_allocation: int
    description: Optional[str] = None
    encashable: bool = False
    created_by: Optional[str] = None  # Auto-populated from authenticated user
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreateCompanyLeaveRequestDTO':
        """Create DTO from dictionary"""
        return cls(
            leave_name=data['leave_name'],
            accrual_type=data.get('accrual_type', 'annually'),
            annual_allocation=int(data['annual_allocation']),
            description=data.get('description'),
            encashable=data.get('encashable', False),
            created_by=data.get('created_by')  # Optional, will be populated by service
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'leave_name': self.leave_name,
            'accrual_type': self.accrual_type,
            'annual_allocation': self.annual_allocation,
            'description': self.description,
            'created_by': self.created_by,
            'encashable': self.encashable
        }
    
    def validate(self) -> List[str]:
        """Validate DTO data and return list of errors"""
        errors = []
        
        if not self.leave_name or not self.leave_name.strip():
            errors.append("Leave name is required")
        
        if not self.accrual_type or not self.accrual_type.strip():
            errors.append("Accrual type is required")
        
        if self.annual_allocation < 0:
            errors.append("Annual allocation cannot be negative")
        
        # Note: created_by is optional and will be auto-populated from authenticated user
        
        return errors


@dataclass
class UpdateCompanyLeaveRequestDTO:
    """
    DTO for company leave update request.
    """
    
    updated_by: str
    leave_name: Optional[str] = None
    accrual_type: Optional[str] = None
    annual_allocation: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    encashable: Optional[bool] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UpdateCompanyLeaveRequestDTO':
        """Create DTO from dictionary"""
        return cls(
            leave_name=data.get('leave_name'),
            accrual_type=data.get('accrual_type'),
            annual_allocation=data.get('annual_allocation'),
            description=data.get('description'),
            is_active=data.get('is_active'),
            updated_by=data['updated_by'],
            encashable=data.get('encashable')
        )
    
    def validate(self) -> List[str]:
        """Validate update data"""
        errors = []
        
        if not self.updated_by or not self.updated_by.strip():
            errors.append("Updated by is required")
        
        if self.annual_allocation is not None and self.annual_allocation < 0:
            errors.append("Annual allocation cannot be negative")
        
        return errors


@dataclass
class CompanyLeaveSearchFiltersDTO:
    """
    DTO for company leave search filters.
    """
    
    is_active: Optional[bool] = None
    accrual_type: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'is_active': self.is_active,
            'accrual_type': self.accrual_type,
            'sort_by': self.sort_by,
            'sort_order': self.sort_order,
            'page': self.page,
            'page_size': self.page_size
        }


@dataclass
class CompanyLeaveResponseDTO:
    """
    DTO for company leave response.
    """
    
    company_leave_id: str
    leave_name: str
    accrual_type: str
    annual_allocation: int
    computed_monthly_allocation: int
    is_active: bool
    description: Optional[str]
    encashable: bool
    created_at: str
    updated_at: str
    created_by: Optional[str]
    updated_by: Optional[str]
    
    @classmethod
    def from_entity(cls, company_leave) -> 'CompanyLeaveResponseDTO':
        """Create DTO from CompanyLeave entity"""
        return cls(
            company_leave_id=company_leave.company_leave_id,
            leave_name=company_leave.leave_name,
            accrual_type=company_leave.accrual_type,
            annual_allocation=company_leave.annual_allocation,
            computed_monthly_allocation=company_leave.computed_monthly_allocation,
            is_active=company_leave.is_active,
            description=company_leave.description,
            encashable=company_leave.encashable,
            created_at=company_leave.created_at.isoformat(),
            updated_at=company_leave.updated_at.isoformat(),
            created_by=company_leave.created_by,
            updated_by=company_leave.updated_by
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary for API response"""    
        return {
            'company_leave_id': self.company_leave_id,
            'leave_name': self.leave_name,
            'accrual_type': self.accrual_type,
            'annual_allocation': self.annual_allocation,
            'computed_monthly_allocation': self.computed_monthly_allocation,
            'is_active': self.is_active,
            'description': self.description,
            'encashable': self.encashable,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }


@dataclass
class CompanyLeaveSummaryDTO:
    """
    DTO for company leave summary (simplified view).
    """
    
    company_leave_id: str
    leave_name: str
    annual_allocation: int
    is_active: bool
    
    @classmethod
    def from_entity(cls, company_leave) -> 'CompanyLeaveSummaryDTO':
        """Create summary DTO from CompanyLeave entity"""
        return cls(
            company_leave_id=company_leave.company_leave_id,
            leave_name=company_leave.leave_name,
            annual_allocation=company_leave.annual_allocation,
            is_active=company_leave.is_active
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary for API response"""
        return {
            'company_leave_id': self.company_leave_id,
            'leave_name': self.leave_name,
            'annual_allocation': self.annual_allocation,
            'is_active': self.is_active
        }


@dataclass
class CompanyLeaveListResponseDTO:
    """
    DTO for company leave list response.
    """
    
    items: List[CompanyLeaveResponseDTO]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'items': [item.to_dict() for item in self.items],
            'total': self.total,
            'page': self.page,
            'page_size': self.page_size,
            'total_pages': self.total_pages
        }


@dataclass
class BulkCompanyLeaveUpdateDTO:
    """
    DTO for bulk company leave updates.
    """
    
    company_leave_id: str
    updates: Dict[str, Any]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BulkCompanyLeaveUpdateDTO':
        """Create DTO from dictionary"""
        return cls(
            company_leave_id=data['company_leave_id'],
            updates=data.get('updates', {})
        )


@dataclass
class BulkCompanyLeaveUpdateResultDTO:
    """
    DTO for bulk company leave update results.
    """
    
    successful_updates: List[str]
    failed_updates: List[Dict[str, Any]]
    total_processed: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'successful_updates': self.successful_updates,
            'failed_updates': self.failed_updates,
            'total_processed': self.total_processed
        }


@dataclass
class CompanyLeaveStatisticsDTO:
    """
    DTO for company leave statistics.
    """
    
    total_leave_types: int
    active_leave_types: int
    inactive_leave_types: int
    total_allocation_days: int
    average_allocation: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'total_leave_types': self.total_leave_types,
            'active_leave_types': self.active_leave_types,
            'inactive_leave_types': self.inactive_leave_types,
            'total_allocation_days': self.total_allocation_days,
            'average_allocation': self.average_allocation
        }


@dataclass
class CompanyLeaveAnalyticsDTO:
    """
    DTO for company leave analytics.
    """
    
    leave_usage_trends: Dict[str, Any]
    popular_leave_types: List[Dict[str, Any]]
    seasonal_patterns: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'leave_usage_trends': self.leave_usage_trends,
            'popular_leave_types': self.popular_leave_types,
            'seasonal_patterns': self.seasonal_patterns
        }


# Exception classes
class CompanyLeaveDTOError(Exception):
    """Base exception for company leave DTO operations"""
    pass


class InvalidCompanyLeaveDataError(CompanyLeaveDTOError):
    """Exception for invalid company leave data"""
    
    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid {field}: {value} - {reason}")


class CompanyLeaveDTOValidationError(CompanyLeaveDTOError):
    """Exception for company leave DTO validation errors"""
    
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation errors: {', '.join(errors)}")


class CompanyLeaveValidationError(Exception):
    """Exception for company leave validation errors"""
    pass


class CompanyLeaveBusinessRuleError(Exception):
    """Exception for business rule violations"""
    pass


class CompanyLeaveNotFoundError(Exception):
    """Exception for when company leave is not found"""
    pass


class CompanyLeaveConflictError(Exception):
    """Exception for company leave conflicts"""
    pass 