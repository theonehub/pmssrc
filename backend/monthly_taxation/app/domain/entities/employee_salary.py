"""
Employee Salary Domain Entity
Manages employee salary structure assignments
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from decimal import Decimal

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.salary_structure_id import SalaryStructureId
from app.domain.value_objects.component_id import ComponentId
from app.domain.exceptions.employee_salary_exceptions import EmployeeSalaryValidationError


@dataclass
class ComponentAssignment:
    """
    Individual component assignment for an employee.
    """
    component_id: ComponentId
    component_code: str
    value: Optional[Decimal] = None
    formula_override: Optional[str] = None
    is_active: bool = True
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    
    def is_effective_on(self, check_date: date) -> bool:
        """Check if this assignment is effective on given date"""
        if self.effective_from and check_date < self.effective_from:
            return False
        if self.effective_to and check_date > self.effective_to:
            return False
        return self.is_active


@dataclass
class SalaryRevision:
    """
    Represents a salary revision with effective dates.
    """
    revision_id: str
    effective_from: date
    effective_to: Optional[date]
    gross_salary: Decimal
    component_assignments: List[ComponentAssignment]
    revision_reason: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    is_active: bool = True
    
    def is_current_revision(self, check_date: date = None) -> bool:
        """Check if this is the current active revision"""
        if not self.is_active:
            return False
        
        check_date = check_date or date.today()
        
        if check_date < self.effective_from:
            return False
        
        if self.effective_to and check_date > self.effective_to:
            return False
            
        return True


@dataclass
class EmployeeSalary:
    """
    Domain entity representing an employee's salary structure and history.
    
    Business Rules:
    - Employee can have only one active salary structure at a time
    - Salary revisions must not have overlapping date ranges
    - All component assignments must reference valid components
    - Gross salary should match sum of earning components
    """
    
    id: SalaryStructureId
    employee_id: EmployeeId
    employee_code: str
    current_gross_salary: Decimal
    currency: str = "INR"
    salary_cycle: str = "MONTHLY"  # MONTHLY, QUARTERLY, ANNUALLY
    revisions: List[SalaryRevision] = field(default_factory=list)
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
        id: SalaryStructureId,
        employee_id: EmployeeId,
        employee_code: str,
        initial_gross_salary: Decimal,
        initial_components: List[ComponentAssignment],
        effective_from: date,
        created_by: str,
        currency: str = "INR"
    ) -> 'EmployeeSalary':
        """Factory method to create new employee salary structure"""
        
        # Create initial revision
        initial_revision = SalaryRevision(
            revision_id=f"REV001",
            effective_from=effective_from,
            effective_to=None,
            gross_salary=initial_gross_salary,
            component_assignments=initial_components,
            revision_reason="Initial salary structure",
            approved_by=created_by,
            approved_at=datetime.utcnow()
        )
        
        return cls(
            id=id,
            employee_id=employee_id,
            employee_code=employee_code,
            current_gross_salary=initial_gross_salary,
            currency=currency,
            revisions=[initial_revision],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            created_by=created_by
        )
    
    def add_revision(
        self,
        new_gross_salary: Decimal,
        new_components: List[ComponentAssignment],
        effective_from: date,
        revision_reason: str,
        approved_by: str,
        effective_to: Optional[date] = None
    ) -> 'EmployeeSalary':
        """Add a new salary revision"""
        
        # Validate dates
        if effective_from <= date.today():
            raise EmployeeSalaryValidationError(
                "Revision effective date must be in the future"
            )
        
        # Close current revision
        current_revision = self.get_current_revision()
        if current_revision:
            current_revision.effective_to = effective_from
        
        # Create new revision
        revision_number = len(self.revisions) + 1
        new_revision = SalaryRevision(
            revision_id=f"REV{revision_number:03d}",
            effective_from=effective_from,
            effective_to=effective_to,
            gross_salary=new_gross_salary,
            component_assignments=new_components,
            revision_reason=revision_reason,
            approved_by=approved_by,
            approved_at=datetime.utcnow()
        )
        
        self.revisions.append(new_revision)
        self.current_gross_salary = new_gross_salary
        self.updated_at = datetime.utcnow()
        
        self._validate_business_rules()
        return self
    
    def get_current_revision(self, as_of_date: date = None) -> Optional[SalaryRevision]:
        """Get the current active revision"""
        as_of_date = as_of_date or date.today()
        
        for revision in self.revisions:
            if revision.is_current_revision(as_of_date):
                return revision
        
        return None
    
    def get_effective_components(self, as_of_date: date = None) -> List[ComponentAssignment]:
        """Get components effective on given date"""
        current_revision = self.get_current_revision(as_of_date)
        if not current_revision:
            return []
        
        as_of_date = as_of_date or date.today()
        return [
            comp for comp in current_revision.component_assignments
            if comp.is_effective_on(as_of_date)
        ]
    
    def get_component_value(self, component_code: str, as_of_date: date = None) -> Optional[Decimal]:
        """Get value for a specific component"""
        effective_components = self.get_effective_components(as_of_date)
        
        for comp in effective_components:
            if comp.component_code == component_code:
                return comp.value
        
        return None
    
    def update_component_value(
        self,
        component_code: str,
        new_value: Decimal,
        effective_from: date,
        updated_by: str
    ) -> 'EmployeeSalary':
        """Update a component value with new effective date"""
        
        current_revision = self.get_current_revision()
        if not current_revision:
            raise EmployeeSalaryValidationError("No active salary revision found")
        
        # Find the component
        component_found = False
        for comp in current_revision.component_assignments:
            if comp.component_code == component_code:
                # End current assignment
                comp.effective_to = effective_from
                
                # Create new assignment
                new_assignment = ComponentAssignment(
                    component_id=comp.component_id,
                    component_code=component_code,
                    value=new_value,
                    formula_override=comp.formula_override,
                    effective_from=effective_from
                )
                current_revision.component_assignments.append(new_assignment)
                component_found = True
                break
        
        if not component_found:
            raise EmployeeSalaryValidationError(f"Component {component_code} not found")
        
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
        
        return self
    
    def deactivate(self, effective_date: date, updated_by: str) -> 'EmployeeSalary':
        """Deactivate salary structure"""
        self.is_active = False
        
        # End all active revisions
        for revision in self.revisions:
            if revision.is_current_revision():
                revision.effective_to = effective_date
                revision.is_active = False
        
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
        
        return self
    
    def calculate_gross_from_components(self, as_of_date: date = None) -> Decimal:
        """Calculate gross salary from active earning components"""
        effective_components = self.get_effective_components(as_of_date)
        
        total = Decimal('0')
        for comp in effective_components:
            if comp.value:
                # Assume all components with values are earnings for this calculation
                # In real implementation, would need component type information
                total += comp.value
        
        return total
    
    def validate_component_assignments(self) -> List[str]:
        """Validate that component assignments are consistent"""
        errors = []
        
        for revision in self.revisions:
            if not revision.is_active:
                continue
                
            # Check for duplicate components in same revision
            component_codes = [comp.component_code for comp in revision.component_assignments]
            duplicates = set([code for code in component_codes if component_codes.count(code) > 1])
            
            if duplicates:
                errors.append(f"Duplicate components in revision {revision.revision_id}: {duplicates}")
            
            # Check that all components have either value or formula
            for comp in revision.component_assignments:
                if comp.value is None and comp.formula_override is None:
                    errors.append(
                        f"Component {comp.component_code} has neither value nor formula"
                    )
        
        return errors
    
    def _validate_business_rules(self):
        """Validate all business rules for employee salary"""
        errors = []
        
        # Validate basic fields
        if self.current_gross_salary <= 0:
            errors.append("Gross salary must be positive")
        
        if not self.currency or len(self.currency) != 3:
            errors.append("Currency must be a valid 3-letter code")
        
        # Validate revisions
        if not self.revisions:
            errors.append("Employee must have at least one salary revision")
        
        # Check for overlapping revisions
        for i, revision1 in enumerate(self.revisions):
            for j, revision2 in enumerate(self.revisions[i+1:], i+1):
                if self._revisions_overlap(revision1, revision2):
                    errors.append(
                        f"Revisions {revision1.revision_id} and {revision2.revision_id} have overlapping dates"
                    )
        
        # Validate component assignments
        component_errors = self.validate_component_assignments()
        errors.extend(component_errors)
        
        if errors:
            raise EmployeeSalaryValidationError("Employee salary validation failed", errors)
    
    def _revisions_overlap(self, rev1: SalaryRevision, rev2: SalaryRevision) -> bool:
        """Check if two revisions have overlapping date ranges"""
        if not rev1.is_active or not rev2.is_active:
            return False
        
        # Get effective end dates
        end1 = rev1.effective_to or date(9999, 12, 31)
        end2 = rev2.effective_to or date(9999, 12, 31)
        
        # Check for overlap
        return not (rev1.effective_from > end2 or rev2.effective_from > end1)
    
    def is_new(self) -> bool:
        """Check if this is a new salary structure (not persisted yet)"""
        return self.created_at is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary for serialization"""
        return {
            "id": str(self.id.value),
            "employee_id": str(self.employee_id.value),
            "employee_code": self.employee_code,
            "current_gross_salary": float(self.current_gross_salary),
            "currency": self.currency,
            "salary_cycle": self.salary_cycle,
            "revisions": [
                {
                    "revision_id": rev.revision_id,
                    "effective_from": rev.effective_from.isoformat(),
                    "effective_to": rev.effective_to.isoformat() if rev.effective_to else None,
                    "gross_salary": float(rev.gross_salary),
                    "component_assignments": [
                        {
                            "component_id": str(comp.component_id.value),
                            "component_code": comp.component_code,
                            "value": float(comp.value) if comp.value else None,
                            "formula_override": comp.formula_override,
                            "is_active": comp.is_active,
                            "effective_from": comp.effective_from.isoformat() if comp.effective_from else None,
                            "effective_to": comp.effective_to.isoformat() if comp.effective_to else None
                        }
                        for comp in rev.component_assignments
                    ],
                    "revision_reason": rev.revision_reason,
                    "approved_by": rev.approved_by,
                    "approved_at": rev.approved_at.isoformat() if rev.approved_at else None,
                    "is_active": rev.is_active
                }
                for rev in self.revisions
            ],
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "metadata": self.metadata
        } 