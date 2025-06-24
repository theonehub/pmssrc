"""
Salary Component DTOs
Data Transfer Objects for salary component operations
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class ComponentTypeDTO(Enum):
    """DTO enum for component types"""
    EARNING = "EARNING"
    DEDUCTION = "DEDUCTION"
    REIMBURSEMENT = "REIMBURSEMENT"


class ValueTypeDTO(Enum):
    """DTO enum for value types"""
    FIXED = "FIXED"
    FORMULA = "FORMULA"
    VARIABLE = "VARIABLE"


class ExemptionSectionDTO(Enum):
    """DTO enum for exemption sections"""
    SECTION_10_13A = "10(13A)"
    SECTION_10_14 = "10(14)"
    SECTION_10_5 = "10(5)"
    SECTION_17_2 = "17(2)"
    NONE = "NONE"


@dataclass
class CreateSalaryComponentDTO:
    """DTO for creating a new salary component"""
    
    # Required fields
    code: str
    name: str
    component_type: str
    value_type: str
    is_taxable: bool
    
    # Optional fields
    exemption_section: str = "NONE"
    formula: Optional[str] = None
    default_value: Optional[float] = None
    description: Optional[str] = None
    
    def validate(self) -> List[str]:
        """Validate the request data"""
        errors = []
        
        if not self.code or not self.code.strip():
            errors.append("Component code is required")
        
        if not self.name or not self.name.strip():
            errors.append("Component name is required")
        
        return errors


@dataclass
class UpdateSalaryComponentDTO:
    """DTO for updating an existing salary component"""
    
    # Optional fields that can be updated
    name: Optional[str] = None
    code: Optional[str] = None
    component_type: Optional[str] = None
    value_type: Optional[str] = None
    is_taxable: Optional[bool] = None
    exemption_section: Optional[str] = None
    formula: Optional[str] = None
    default_value: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    
    def validate(self) -> List[str]:
        """Validate the update data"""
        errors = []
        
        # Validate exemption section if provided
        if self.exemption_section is not None:
            try:
                ExemptionSectionDTO(self.exemption_section.upper())
            except (ValueError, AttributeError):
                errors.append(f"Invalid exemption section: {self.exemption_section}")
        
        return errors


@dataclass
class SalaryComponentSearchFiltersDTO:
    """DTO for salary component search filters"""
    
    # Pagination
    page: int = 1
    page_size: int = 50
    
    # Filters
    component_type: Optional[str] = None
    value_type: Optional[str] = None
    is_taxable: Optional[bool] = None
    is_active: Optional[bool] = None
    search_term: Optional[str] = None  # Search in code, name, description
    
    # Sorting
    sort_by: str = "created_at"
    sort_order: str = "desc"  # asc, desc
    
    def validate(self) -> List[str]:
        """Validate the search filters"""
        errors = []
        
        if self.page < 1:
            errors.append("Page must be at least 1")
        
        if self.page_size < 1 or self.page_size > 100:
            errors.append("Page size must be between 1 and 100")
        
        if self.sort_order not in ["asc", "desc"]:
            errors.append("Sort order must be 'asc' or 'desc'")
        
        return errors


@dataclass
class SalaryComponentResponseDTO:
    """DTO for salary component response"""
    
    id: str
    code: str
    name: str
    component_type: str
    value_type: str
    is_taxable: bool
    exemption_section: str
    formula: Optional[str] = None
    default_value: Optional[float] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "component_type": self.component_type,
            "value_type": self.value_type,
            "is_taxable": self.is_taxable,
            "exemption_section": self.exemption_section,
            "formula": self.formula,
            "default_value": self.default_value,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_entity(cls, entity) -> 'SalaryComponentResponseDTO':
        """Create DTO from domain entity"""
        from app.domain.entities.salary_component import SalaryComponent
        
        return cls(
            id=str(entity.id.value),
            code=entity.code,
            name=entity.name,
            component_type=entity.component_type.value,
            value_type=entity.value_type.value,
            is_taxable=entity.is_taxable,
            exemption_section=entity.exemption_section.value,
            formula=entity.formula,
            default_value=float(entity.default_value) if entity.default_value else None,
            description=entity.description,
            is_active=entity.is_active,
            created_at=entity.created_at.isoformat() if entity.created_at else None,
            updated_at=entity.updated_at.isoformat() if entity.updated_at else None,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            metadata=entity.metadata
        )


@dataclass
class SalaryComponentSummaryDTO:
    """DTO for salary component summary in lists"""
    
    id: str
    code: str
    name: str
    component_type: str
    value_type: str
    is_taxable: bool
    is_active: bool
    created_at: Optional[str] = None
    
    @classmethod
    def from_entity(cls, entity) -> 'SalaryComponentSummaryDTO':
        """Create summary DTO from domain entity"""
        return cls(
            id=str(entity.id.value),
            code=entity.code,
            name=entity.name,
            component_type=entity.component_type.value,
            value_type=entity.value_type.value,
            is_taxable=entity.is_taxable,
            is_active=entity.is_active,
            created_at=entity.created_at.isoformat() if entity.created_at else None
        )


@dataclass
class SalaryComponentListResponseDTO:
    """DTO for paginated salary component list response"""
    
    components: List[SalaryComponentSummaryDTO]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


@dataclass
class FormulaValidationRequestDTO:
    """DTO for formula validation request"""
    
    formula: str
    component_context: Optional[Dict[str, float]] = None  # For testing formula with sample values
    
    def validate(self) -> List[str]:
        """Validate the request"""
        errors = []
        
        if not self.formula or not self.formula.strip():
            errors.append("Formula is required")
        
        return errors


@dataclass
class FormulaValidationResponseDTO:
    """DTO for formula validation response"""
    
    is_valid: bool
    error_message: Optional[str] = None
    referenced_components: List[str] = None
    test_result: Optional[float] = None  # If test values provided
    
    
@dataclass
class ComponentUsageStatsDTO:
    """DTO for component usage statistics"""
    
    component_id: str
    component_code: str
    component_name: str
    usage_count: int  # Number of employees using this component
    active_assignments: int  # Current active assignments
    total_assignments: int  # All time assignments
    last_used: Optional[str] = None  # Last assignment date


# Custom exceptions for DTO validation
class SalaryComponentValidationError(Exception):
    """Raised when salary component DTO validation fails"""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []


class SalaryComponentBusinessRuleError(Exception):
    """Raised when business rule validation fails"""
    
    def __init__(self, message: str, rule: str = None):
        super().__init__(message)
        self.rule = rule


class SalaryComponentNotFoundError(Exception):
    """Raised when salary component is not found"""
    
    def __init__(self, component_id: str):
        super().__init__(f"Salary component not found: {component_id}")
        self.component_id = component_id


class SalaryComponentConflictError(Exception):
    """Raised when salary component operation conflicts with existing data"""
    
    def __init__(self, message: str, conflict_field: str = None):
        super().__init__(message)
        self.conflict_field = conflict_field 