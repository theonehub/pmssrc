"""
Company Leave Data Transfer Objects
DTOs for company leave-related operations
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

from domain.value_objects.leave_type import LeaveType, LeaveCategory
from domain.value_objects.leave_policy import LeavePolicy, AccrualType


@dataclass
class CompanyLeaveCreateRequestDTO:
    """
    DTO for company leave creation request.
    
    Follows SOLID principles:
    - SRP: Only handles company leave creation request data
    - OCP: Can be extended with new fields without breaking existing code
    - LSP: Can be substituted with other request DTOs
    - ISP: Contains only company leave creation related fields
    - DIP: Doesn't depend on concrete implementations
    """
    
    leave_type_code: str
    leave_type_name: str
    leave_category: str
    annual_allocation: int
    accrual_type: str = "annually"
    description: Optional[str] = None
    
    # Policy configuration
    max_carryover_days: Optional[int] = None
    min_advance_notice_days: Optional[int] = None
    max_continuous_days: Optional[int] = None
    requires_approval: bool = True
    auto_approve_threshold: Optional[int] = None
    requires_medical_certificate: bool = False
    medical_certificate_threshold: Optional[int] = None
    is_encashable: bool = False
    max_encashment_days: Optional[int] = None
    available_during_probation: bool = True
    probation_allocation: Optional[int] = None
    gender_specific: Optional[str] = None
    
    # Metadata
    created_by: str
    effective_from: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyLeaveCreateRequestDTO':
        """Create DTO from dictionary"""
        return cls(
            leave_type_code=data['leave_type_code'],
            leave_type_name=data['leave_type_name'],
            leave_category=data['leave_category'],
            annual_allocation=int(data['annual_allocation']),
            accrual_type=data.get('accrual_type', 'annually'),
            description=data.get('description'),
            max_carryover_days=data.get('max_carryover_days'),
            min_advance_notice_days=data.get('min_advance_notice_days'),
            max_continuous_days=data.get('max_continuous_days'),
            requires_approval=data.get('requires_approval', True),
            auto_approve_threshold=data.get('auto_approve_threshold'),
            requires_medical_certificate=data.get('requires_medical_certificate', False),
            medical_certificate_threshold=data.get('medical_certificate_threshold'),
            is_encashable=data.get('is_encashable', False),
            max_encashment_days=data.get('max_encashment_days'),
            available_during_probation=data.get('available_during_probation', True),
            probation_allocation=data.get('probation_allocation'),
            gender_specific=data.get('gender_specific'),
            created_by=data['created_by'],
            effective_from=data.get('effective_from')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'leave_type_code': self.leave_type_code,
            'leave_type_name': self.leave_type_name,
            'leave_category': self.leave_category,
            'annual_allocation': self.annual_allocation,
            'accrual_type': self.accrual_type,
            'description': self.description,
            'max_carryover_days': self.max_carryover_days,
            'min_advance_notice_days': self.min_advance_notice_days,
            'max_continuous_days': self.max_continuous_days,
            'requires_approval': self.requires_approval,
            'auto_approve_threshold': self.auto_approve_threshold,
            'requires_medical_certificate': self.requires_medical_certificate,
            'medical_certificate_threshold': self.medical_certificate_threshold,
            'is_encashable': self.is_encashable,
            'max_encashment_days': self.max_encashment_days,
            'available_during_probation': self.available_during_probation,
            'probation_allocation': self.probation_allocation,
            'gender_specific': self.gender_specific,
            'created_by': self.created_by,
            'effective_from': self.effective_from
        }
    
    def validate(self) -> List[str]:
        """Validate DTO data and return list of errors"""
        errors = []
        
        if not self.leave_type_code or not self.leave_type_code.strip():
            errors.append("Leave type code is required")
        
        if not self.leave_type_name or not self.leave_type_name.strip():
            errors.append("Leave type name is required")
        
        if not self.leave_category or not self.leave_category.strip():
            errors.append("Leave category is required")
        
        if self.annual_allocation < 0:
            errors.append("Annual allocation cannot be negative")
        
        if not self.created_by or not self.created_by.strip():
            errors.append("Created by is required")
        
        # Validate leave category
        try:
            LeaveCategory(self.leave_category.lower())
        except ValueError:
            errors.append(f"Invalid leave category: {self.leave_category}")
        
        # Validate accrual type
        try:
            AccrualType(self.accrual_type.lower())
        except ValueError:
            errors.append(f"Invalid accrual type: {self.accrual_type}")
        
        # Validate carryover days
        if self.max_carryover_days is not None:
            if self.max_carryover_days < 0:
                errors.append("Max carryover days cannot be negative")
            elif self.max_carryover_days > self.annual_allocation:
                errors.append("Max carryover days cannot exceed annual allocation")
        
        # Validate advance notice days
        if self.min_advance_notice_days is not None and self.min_advance_notice_days < 0:
            errors.append("Min advance notice days cannot be negative")
        
        # Validate continuous days
        if self.max_continuous_days is not None and self.max_continuous_days <= 0:
            errors.append("Max continuous days must be positive if specified")
        
        # Validate auto approve threshold
        if self.auto_approve_threshold is not None and self.auto_approve_threshold <= 0:
            errors.append("Auto approve threshold must be positive if specified")
        
        # Validate medical certificate threshold
        if self.medical_certificate_threshold is not None and self.medical_certificate_threshold <= 0:
            errors.append("Medical certificate threshold must be positive if specified")
        
        # Validate encashment days
        if self.max_encashment_days is not None:
            if self.max_encashment_days < 0:
                errors.append("Max encashment days cannot be negative")
            elif self.max_encashment_days > self.annual_allocation:
                errors.append("Max encashment days cannot exceed annual allocation")
        
        # Validate probation allocation
        if self.probation_allocation is not None and self.probation_allocation < 0:
            errors.append("Probation allocation cannot be negative")
        
        # Validate gender specific
        if self.gender_specific and self.gender_specific not in ['male', 'female']:
            errors.append("Gender specific must be 'male', 'female', or None")
        
        return errors


@dataclass
class CompanyLeaveUpdateRequestDTO:
    """
    DTO for company leave update request.
    """
    
    leave_type_name: Optional[str] = None
    annual_allocation: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    
    # Policy updates
    max_carryover_days: Optional[int] = None
    min_advance_notice_days: Optional[int] = None
    max_continuous_days: Optional[int] = None
    requires_approval: Optional[bool] = None
    auto_approve_threshold: Optional[int] = None
    requires_medical_certificate: Optional[bool] = None
    medical_certificate_threshold: Optional[int] = None
    is_encashable: Optional[bool] = None
    max_encashment_days: Optional[int] = None
    available_during_probation: Optional[bool] = None
    probation_allocation: Optional[int] = None
    
    # Metadata
    updated_by: str
    update_reason: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompanyLeaveUpdateRequestDTO':
        """Create DTO from dictionary"""
        return cls(
            leave_type_name=data.get('leave_type_name'),
            annual_allocation=data.get('annual_allocation'),
            description=data.get('description'),
            is_active=data.get('is_active'),
            max_carryover_days=data.get('max_carryover_days'),
            min_advance_notice_days=data.get('min_advance_notice_days'),
            max_continuous_days=data.get('max_continuous_days'),
            requires_approval=data.get('requires_approval'),
            auto_approve_threshold=data.get('auto_approve_threshold'),
            requires_medical_certificate=data.get('requires_medical_certificate'),
            medical_certificate_threshold=data.get('medical_certificate_threshold'),
            is_encashable=data.get('is_encashable'),
            max_encashment_days=data.get('max_encashment_days'),
            available_during_probation=data.get('available_during_probation'),
            probation_allocation=data.get('probation_allocation'),
            updated_by=data['updated_by'],
            update_reason=data.get('update_reason')
        )
    
    def validate(self) -> List[str]:
        """Validate update data"""
        errors = []
        
        if not self.updated_by or not self.updated_by.strip():
            errors.append("Updated by is required")
        
        if self.annual_allocation is not None and self.annual_allocation < 0:
            errors.append("Annual allocation cannot be negative")
        
        if self.max_carryover_days is not None and self.max_carryover_days < 0:
            errors.append("Max carryover days cannot be negative")
        
        if self.min_advance_notice_days is not None and self.min_advance_notice_days < 0:
            errors.append("Min advance notice days cannot be negative")
        
        if self.max_continuous_days is not None and self.max_continuous_days <= 0:
            errors.append("Max continuous days must be positive if specified")
        
        if self.auto_approve_threshold is not None and self.auto_approve_threshold <= 0:
            errors.append("Auto approve threshold must be positive if specified")
        
        if self.medical_certificate_threshold is not None and self.medical_certificate_threshold <= 0:
            errors.append("Medical certificate threshold must be positive if specified")
        
        if self.max_encashment_days is not None and self.max_encashment_days < 0:
            errors.append("Max encashment days cannot be negative")
        
        if self.probation_allocation is not None and self.probation_allocation < 0:
            errors.append("Probation allocation cannot be negative")
        
        return errors


@dataclass
class CompanyLeaveResponseDTO:
    """
    DTO for company leave response.
    """
    
    company_leave_id: str
    leave_type: Dict[str, Any]
    policy: Dict[str, Any]
    is_active: bool
    description: Optional[str]
    effective_from: Optional[str]
    effective_until: Optional[str]
    created_at: str
    updated_at: str
    created_by: Optional[str]
    updated_by: Optional[str]
    
    @classmethod
    def from_entity(cls, company_leave) -> 'CompanyLeaveResponseDTO':
        """Create DTO from CompanyLeave entity"""
        return cls(
            company_leave_id=company_leave.company_leave_id,
            leave_type={
                'code': company_leave.leave_type.code,
                'name': company_leave.leave_type.name,
                'category': company_leave.leave_type.category.value,
                'description': company_leave.leave_type.description
            },
            policy={
                'annual_allocation': company_leave.policy.annual_allocation,
                'accrual_type': company_leave.policy.accrual_type.value,
                'accrual_rate': float(company_leave.policy.accrual_rate) if company_leave.policy.accrual_rate else None,
                'max_carryover_days': company_leave.policy.max_carryover_days,
                'carryover_expiry_months': company_leave.policy.carryover_expiry_months,
                'min_advance_notice_days': company_leave.policy.min_advance_notice_days,
                'max_advance_application_days': company_leave.policy.max_advance_application_days,
                'min_application_days': company_leave.policy.min_application_days,
                'max_continuous_days': company_leave.policy.max_continuous_days,
                'requires_approval': company_leave.policy.requires_approval,
                'auto_approve_threshold': company_leave.policy.auto_approve_threshold,
                'requires_medical_certificate': company_leave.policy.requires_medical_certificate,
                'medical_certificate_threshold': company_leave.policy.medical_certificate_threshold,
                'is_encashable': company_leave.policy.is_encashable,
                'max_encashment_days': company_leave.policy.max_encashment_days,
                'encashment_percentage': float(company_leave.policy.encashment_percentage),
                'available_during_probation': company_leave.policy.available_during_probation,
                'probation_allocation': company_leave.policy.probation_allocation,
                'gender_specific': company_leave.policy.gender_specific,
                'employee_category_specific': company_leave.policy.employee_category_specific
            },
            is_active=company_leave.is_active,
            description=company_leave.description,
            effective_from=company_leave.effective_from.isoformat() if company_leave.effective_from else None,
            effective_until=company_leave.effective_until.isoformat() if company_leave.effective_until else None,
            created_at=company_leave.created_at.isoformat(),
            updated_at=company_leave.updated_at.isoformat(),
            created_by=company_leave.created_by,
            updated_by=company_leave.updated_by
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary for API response"""
        return {
            'company_leave_id': self.company_leave_id,
            'leave_type': self.leave_type,
            'policy': self.policy,
            'is_active': self.is_active,
            'description': self.description,
            'effective_from': self.effective_from,
            'effective_until': self.effective_until,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }


@dataclass
class CompanyLeaveSummaryDTO:
    """
    DTO for company leave summary (lightweight version).
    """
    
    company_leave_id: str
    leave_type_code: str
    leave_type_name: str
    leave_category: str
    annual_allocation: int
    is_active: bool
    
    @classmethod
    def from_entity(cls, company_leave) -> 'CompanyLeaveSummaryDTO':
        """Create summary DTO from CompanyLeave entity"""
        return cls(
            company_leave_id=company_leave.company_leave_id,
            leave_type_code=company_leave.leave_type.code,
            leave_type_name=company_leave.leave_type.name,
            leave_category=company_leave.leave_type.category.value,
            annual_allocation=company_leave.policy.annual_allocation,
            is_active=company_leave.is_active
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'company_leave_id': self.company_leave_id,
            'leave_type_code': self.leave_type_code,
            'leave_type_name': self.leave_type_name,
            'leave_category': self.leave_category,
            'annual_allocation': self.annual_allocation,
            'is_active': self.is_active
        }


@dataclass
class LeaveTypeOptionsDTO:
    """
    DTO for leave type options (for dropdowns, etc.).
    """
    
    code: str
    name: str
    category: str
    description: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert DTO to dictionary"""
        return {
            'code': self.code,
            'name': self.name,
            'category': self.category,
            'description': self.description
        }


# Validation utilities
def validate_leave_type_code(code: str) -> bool:
    """Validate leave type code format"""
    if not code or len(code) > 10:
        return False
    return code.replace('_', '').replace('-', '').isalnum()


def validate_leave_category(category: str) -> bool:
    """Validate leave category"""
    try:
        LeaveCategory(category.lower())
        return True
    except ValueError:
        return False


def validate_accrual_type(accrual_type: str) -> bool:
    """Validate accrual type"""
    try:
        AccrualType(accrual_type.lower())
        return True
    except ValueError:
        return False


class CompanyLeaveDTOError(Exception):
    """Base exception for company leave DTO operations"""
    pass


class InvalidCompanyLeaveDataError(CompanyLeaveDTOError):
    """Exception raised when company leave data is invalid"""
    
    def __init__(self, field: str, value: Any, reason: str):
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid {field} '{value}': {reason}")


class CompanyLeaveDTOValidationError(CompanyLeaveDTOError):
    """Exception raised when DTO validation fails"""
    
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}") 