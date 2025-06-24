"""
Company Salary Structure Configuration
Wrapper entity for company-controlled salary components
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from decimal import Decimal

from app.domain.value_objects.money import Money
from app.domain.value_objects.employee_id import EmployeeId
from app.domain.entities.taxation.salary_income import SalaryIncome, SpecificAllowances


@dataclass
class CompanySalaryStructure:
    """
    Company-defined salary structure that admins can configure.
    Uses existing SalaryIncome computation logic.
    """
    
    # Company identifiers
    organization_id: str
    structure_name: str
    effective_from_date: str
    
    # Company-controlled components (defaults that admin sets)
    default_basic_salary: Money = Money.zero()
    default_dearness_allowance: Money = Money.zero()
    default_special_allowance: Money = Money.zero()
    
    # Company HRA policy
    company_hra_policy: Dict[str, Any] = field(default_factory=dict)
    
    # Company allowance policies (using existing 40+ allowances)
    company_allowance_policies: Dict[str, Money] = field(default_factory=dict)
    
    # Company perquisites policies
    company_perquisites_enabled: bool = True
    
    # Metadata
    created_by: str = ""
    updated_by: str = ""
    is_active: bool = True
    
    def create_employee_salary_income(
        self, 
        employee_id: EmployeeId,
        basic_salary: Money,
        dearness_allowance: Money,
        hra_received: Money,
        hra_city_type: str,
        actual_rent_paid: Money,
        special_allowance: Money,
        is_government_employee: bool = False,
        **kwargs
    ) -> SalaryIncome:
        """
        Create SalaryIncome entity using existing computation logic.
        Company structure provides defaults, but actual values come from payroll.
        """
        
        # Create specific allowances from company policies
        specific_allowances = SpecificAllowances()
        
        # Apply company allowance policies
        for allowance_name, amount in self.company_allowance_policies.items():
            if hasattr(specific_allowances, allowance_name):
                setattr(specific_allowances, allowance_name, amount)
        
        # Use existing SalaryIncome entity - NO COMPUTATION CHANGES
        return SalaryIncome(
            basic_salary=basic_salary,
            dearness_allowance=dearness_allowance,
            hra_received=hra_received,
            hra_city_type=hra_city_type,
            actual_rent_paid=actual_rent_paid,
            special_allowance=special_allowance,
            is_government_employee=is_government_employee,
            specific_allowances=specific_allowances,
            **kwargs
        )
    
    def get_company_allowance_structure(self) -> Dict[str, Any]:
        """Get company allowance structure for admin configuration."""
        return {
            "basic_structure": {
                "default_basic_salary": self.default_basic_salary.to_float(),
                "default_dearness_allowance": self.default_dearness_allowance.to_float(),
                "default_special_allowance": self.default_special_allowance.to_float()
            },
            "hra_policy": self.company_hra_policy,
            "allowance_policies": {
                name: amount.to_float() 
                for name, amount in self.company_allowance_policies.items()
            },
            "structure_metadata": {
                "organization_id": self.organization_id,
                "structure_name": self.structure_name,
                "effective_from": self.effective_from_date,
                "is_active": self.is_active,
                "created_by": self.created_by,
                "updated_by": self.updated_by
            }
        }
    
    def update_allowance_policy(self, allowance_name: str, amount: Money) -> bool:
        """Update specific allowance policy."""
        if allowance_name in [
            'city_compensatory_allowance', 'rural_allowance', 'proctorship_allowance',
            'wardenship_allowance', 'project_allowance', 'deputation_allowance',
            'overtime_allowance', 'interim_relief', 'tiffin_allowance',
            'fixed_medical_allowance', 'servant_allowance', 'hills_allowance',
            'border_allowance', 'transport_employee_allowance', 'children_education_allowance',
            'hostel_allowance', 'disabled_transport_allowance', 'underground_mines_allowance',
            'government_entertainment_allowance', 'any_other_allowance'
        ]:
            self.company_allowance_policies[allowance_name] = amount
            return True
        return False
    
    def validate_structure(self) -> List[str]:
        """Validate company salary structure."""
        warnings = []
        
        if self.default_basic_salary.is_zero():
            warnings.append("Default basic salary not set")
        
        if not self.company_hra_policy:
            warnings.append("HRA policy not configured")
        
        if not self.organization_id:
            warnings.append("Organization ID required")
        
        return warnings


@dataclass 
class EmployeeSalaryAssignment:
    """
    Individual employee salary assignment based on company structure.
    Links company structure to specific employee.
    """
    
    employee_id: EmployeeId
    organization_id: str
    salary_structure_id: str
    
    # Employee-specific overrides
    basic_salary: Money
    dearness_allowance: Money
    special_allowance: Money
    hra_city_type: str
    actual_rent_paid: Money
    
    # Employee-specific flags
    is_government_employee: bool = False
    
    # Assignment metadata
    effective_from: str = ""
    assigned_by: str = ""
    is_active: bool = True
    
    def get_assignment_summary(self) -> Dict[str, Any]:
        """Get employee salary assignment summary."""
        return {
            "employee_id": str(self.employee_id),
            "organization_id": self.organization_id,
            "salary_structure_id": self.salary_structure_id,
            "salary_components": {
                "basic_salary": self.basic_salary.to_float(),
                "dearness_allowance": self.dearness_allowance.to_float(),
                "special_allowance": self.special_allowance.to_float(),
                "hra_city_type": self.hra_city_type,
                "actual_rent_paid": self.actual_rent_paid.to_float()
            },
            "employee_flags": {
                "is_government_employee": self.is_government_employee
            },
            "assignment_metadata": {
                "effective_from": self.effective_from,
                "assigned_by": self.assigned_by,
                "is_active": self.is_active
            }
        } 