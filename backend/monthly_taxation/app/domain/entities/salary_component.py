"""
Salary Component Domain Entity
Core business entity for salary component configuration
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from app.domain.value_objects.component_id import ComponentId
from app.domain.value_objects.component_type import ComponentType, ValueType
from app.domain.exceptions.salary_component_exceptions import SalaryComponentValidationError


class ExemptionSection(Enum):
    """Income tax exemption sections"""
    SECTION_10_13A = "10(13A)"  # HRA
    SECTION_10_14 = "10(14)"    # Special allowances  
    SECTION_10_5 = "10(5)"      # LTA
    SECTION_17_2 = "17(2)"      # Professional tax
    NONE = "NONE"


@dataclass
class SalaryComponent:
    """
    Domain entity representing a salary component configuration.
    
    Business Rules:
    - Component code must be unique within organization
    - Formula components must have valid formula expressions
    - Taxable components cannot have exemption sections unless specifically allowed
    - Component names must be descriptive and professional
    """
    
    id: ComponentId
    code: str
    name: str
    component_type: ComponentType
    value_type: ValueType
    is_taxable: bool
    exemption_section: ExemptionSection
    formula: Optional[str] = None
    default_value: Optional[float] = None
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate business rules after initialization"""
        self._validate_business_rules()
    
    @classmethod
    def create(
        cls,
        id: ComponentId,
        code: str,
        name: str,
        component_type: ComponentType,
        value_type: ValueType,
        is_taxable: bool,
        exemption_section: ExemptionSection = ExemptionSection.NONE,
        formula: Optional[str] = None,
        default_value: Optional[float] = None,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> 'SalaryComponent':
        """Factory method to create a new salary component"""
        
        return cls(
            id=id,
            code=code.upper().strip(),
            name=name.strip(),
            component_type=component_type,
            value_type=value_type,
            is_taxable=is_taxable,
            exemption_section=exemption_section,
            formula=formula.strip() if formula else None,
            default_value=default_value,
            description=description.strip() if description else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=created_by
        )
    
    def update(
        self,
        name: Optional[str] = None,
        is_taxable: Optional[bool] = None,
        exemption_section: Optional[ExemptionSection] = None,
        formula: Optional[str] = None,
        default_value: Optional[float] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
        updated_by: Optional[str] = None
    ) -> 'SalaryComponent':
        """Update component with new values"""
        
        if name is not None:
            self.name = name.strip()
        if is_taxable is not None:
            self.is_taxable = is_taxable
        if exemption_section is not None:
            self.exemption_section = exemption_section
        if formula is not None:
            self.formula = formula.strip() if formula else None
        if default_value is not None:
            self.default_value = default_value
        if description is not None:
            self.description = description.strip() if description else None
        if is_active is not None:
            self.is_active = is_active
        if updated_by is not None:
            self.updated_by = updated_by
            
        self.updated_at = datetime.utcnow()
        self._validate_business_rules()
        return self
    
    def deactivate(self, updated_by: str) -> 'SalaryComponent':
        """Deactivate the component"""
        self.is_active = False
        self.updated_by = updated_by
        self.updated_at = datetime.utcnow()
        return self
    
    def can_be_deleted(self) -> bool:
        """Check if component can be safely deleted"""
        # Business rule: Only inactive components can be deleted
        return not self.is_active
    
    def is_formula_based(self) -> bool:
        """Check if component uses formula for calculation"""
        return self.value_type == ValueType.FORMULA and self.formula is not None
    
    def is_earning(self) -> bool:
        """Check if component is an earning"""
        return self.component_type == ComponentType.EARNING
    
    def is_deduction(self) -> bool:
        """Check if component is a deduction"""
        return self.component_type == ComponentType.DEDUCTION
    
    def is_reimbursement(self) -> bool:
        """Check if component is a reimbursement"""
        return self.component_type == ComponentType.REIMBURSEMENT
    
    def has_exemption(self) -> bool:
        """Check if component has tax exemption"""
        return self.exemption_section != ExemptionSection.NONE
    
    def _validate_business_rules(self):
        """Validate all business rules for the component"""
        errors = []
        
        # Validate code
        if not self.code or len(self.code.strip()) < 2:
            errors.append("Component code must be at least 2 characters long")
        
        if not self.code.replace('_', '').replace('-', '').isalnum():
            errors.append("Component code must contain only alphanumeric characters, hyphens, and underscores")
        
        # Validate name
        if not self.name or len(self.name.strip()) < 3:
            errors.append("Component name must be at least 3 characters long")
        
        # Validate formula for formula-based components
        if self.value_type == ValueType.FORMULA:
            if not self.formula or not self.formula.strip():
                errors.append("Formula is required for formula-based components")
        
        # # Validate default value for fixed components
        # if self.value_type == ValueType.FIXED:
        #     if self.default_value is None or self.default_value < 0:
        #         errors.append("Default value is required for fixed components and must be non-negative")
        
        # Validate exemption section logic
        if not self.is_taxable and self.exemption_section != ExemptionSection.NONE:
            errors.append("Non-taxable components cannot have exemption sections")
        
        # Validate reimbursement components
        if self.component_type == ComponentType.REIMBURSEMENT and self.is_taxable:
            errors.append("Reimbursement components should typically be non-taxable")
        
        if errors:
            raise SalaryComponentValidationError("Component validation failed", errors)
    
    def is_new(self) -> bool:
        """Check if this is a new component (not persisted yet)"""
        return self.created_at is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization"""
        return {
            "id": str(self.id.value),
            "code": self.code,
            "name": self.name,
            "component_type": self.component_type.value,
            "value_type": self.value_type.value,
            "is_taxable": self.is_taxable,
            "exemption_section": self.exemption_section.value,
            "formula": self.formula,
            "default_value": self.default_value,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "metadata": self.metadata
        } 