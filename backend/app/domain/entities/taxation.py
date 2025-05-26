"""
Taxation Domain Entity
Aggregate root for taxation-related operations
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
from datetime import date, datetime
from decimal import Decimal

from domain.value_objects.employee_id import EmployeeId
from domain.value_objects.money import Money
from domain.value_objects.tax_regime import TaxRegime
from domain.events.taxation_events import (
    TaxCalculated, TaxRegimeChanged, DeductionAdded, DeductionRemoved
)


@dataclass
class Taxation:
    """
    Taxation aggregate root following DDD principles.
    
    Follows SOLID principles:
    - SRP: Only handles taxation-related business logic
    - OCP: Can be extended with new tax types without modification
    - LSP: Can be substituted anywhere Taxation is expected
    - ISP: Provides focused taxation operations
    - DIP: Depends on abstractions (value objects, events)
    """
    
    # Identity
    employee_id: EmployeeId
    tax_year: str
    
    # Tax Configuration
    regime: TaxRegime
    
    # Income Information
    gross_annual_salary: Money
    basic_salary: Money = field(default_factory=lambda: Money.zero())
    hra: Money = field(default_factory=lambda: Money.zero())
    special_allowance: Money = field(default_factory=lambda: Money.zero())
    other_allowances: Money = field(default_factory=lambda: Money.zero())
    
    # Deductions
    deductions: Dict[str, Money] = field(default_factory=dict)
    
    # Calculated Values
    taxable_income: Optional[Money] = None
    calculated_tax: Optional[Money] = None
    cess_amount: Optional[Money] = None
    surcharge_amount: Optional[Money] = None
    total_tax_liability: Optional[Money] = None
    
    # Rebates and Relief
    rebate_87a: Money = field(default_factory=lambda: Money.zero())
    
    # System Fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    calculated_at: Optional[datetime] = None
    
    # Domain Events
    _domain_events: List = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Post initialization validation"""
        self._validate_taxation_data()
    
    @classmethod
    def create_new_taxation(
        cls,
        employee_id: EmployeeId,
        tax_year: str,
        regime: TaxRegime,
        gross_annual_salary: Money,
        basic_salary: Optional[Money] = None,
        hra: Optional[Money] = None
    ) -> 'Taxation':
        """Factory method to create new taxation record"""
        
        taxation = cls(
            employee_id=employee_id,
            tax_year=tax_year,
            regime=regime,
            gross_annual_salary=gross_annual_salary,
            basic_salary=basic_salary or Money.zero(),
            hra=hra or Money.zero()
        )
        
        return taxation
    
    def change_regime(self, new_regime: TaxRegime, reason: str):
        """
        Change tax regime.
        
        Business Rules:
        1. Can only change regime before tax calculation is finalized
        2. Must provide reason for change
        3. Changing regime may invalidate existing deductions
        """
        
        if not reason or not reason.strip():
            raise ValueError("Reason for regime change is required")
        
        old_regime = self.regime
        self.regime = new_regime
        self.updated_at = datetime.utcnow()
        
        # Clear calculated values as they need recalculation
        self._clear_calculated_values()
        
        # Remove deductions not allowed in new regime
        self._validate_deductions_for_regime()
        
        # Raise domain event
        self._domain_events.append(
            TaxRegimeChanged(
                employee_id=self.employee_id,
                tax_year=self.tax_year,
                old_regime=old_regime,
                new_regime=new_regime,
                reason=reason,
                occurred_at=datetime.utcnow()
            )
        )
    
    def add_deduction(self, section: str, amount: Money, description: Optional[str] = None):
        """
        Add tax deduction.
        
        Business Rules:
        1. Deduction section must be allowed for current regime
        2. Amount must be positive
        3. Cannot exceed section limits
        """
        
        if not amount.is_positive():
            raise ValueError("Deduction amount must be positive")
        
        if not self._is_deduction_allowed(section):
            raise ValueError(f"Deduction under section {section} is not allowed for {self.regime} regime")
        
        # Validate section limits
        self._validate_deduction_limit(section, amount)
        
        old_amount = self.deductions.get(section, Money.zero())
        self.deductions[section] = amount
        self.updated_at = datetime.utcnow()
        
        # Clear calculated values as they need recalculation
        self._clear_calculated_values()
        
        # Raise domain event
        self._domain_events.append(
            DeductionAdded(
                employee_id=self.employee_id,
                tax_year=self.tax_year,
                section=section,
                amount=amount,
                old_amount=old_amount,
                description=description,
                occurred_at=datetime.utcnow()
            )
        )
    
    def remove_deduction(self, section: str):
        """Remove tax deduction"""
        
        if section not in self.deductions:
            raise ValueError(f"Deduction under section {section} does not exist")
        
        removed_amount = self.deductions.pop(section)
        self.updated_at = datetime.utcnow()
        
        # Clear calculated values as they need recalculation
        self._clear_calculated_values()
        
        # Raise domain event
        self._domain_events.append(
            DeductionRemoved(
                employee_id=self.employee_id,
                tax_year=self.tax_year,
                section=section,
                amount=removed_amount,
                occurred_at=datetime.utcnow()
            )
        )
    
    def calculate_tax(self) -> Money:
        """
        Calculate tax based on current regime and deductions.
        
        This method orchestrates the tax calculation but delegates
        the actual calculation logic to domain services.
        """
        
        # Calculate taxable income
        self.taxable_income = self._calculate_taxable_income()
        
        # Calculate tax based on regime
        self.calculated_tax = self._calculate_income_tax()
        
        # Calculate surcharge
        self.surcharge_amount = self._calculate_surcharge()
        
        # Calculate cess
        self.cess_amount = self._calculate_cess()
        
        # Calculate rebate
        self.rebate_87a = self._calculate_rebate_87a()
        
        # Calculate total tax liability
        self.total_tax_liability = self._calculate_total_tax_liability()
        
        self.calculated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._domain_events.append(
            TaxCalculated(
                employee_id=self.employee_id,
                tax_year=self.tax_year,
                regime=self.regime,
                taxable_income=self.taxable_income,
                calculated_tax=self.calculated_tax,
                total_tax_liability=self.total_tax_liability,
                occurred_at=datetime.utcnow()
            )
        )
        
        return self.total_tax_liability
    
    def get_total_deductions(self) -> Money:
        """Get total deductions amount"""
        total = Money.zero()
        for amount in self.deductions.values():
            total = total.add(amount)
        return total
    
    def get_deduction_by_section(self, section: str) -> Optional[Money]:
        """Get deduction amount for specific section"""
        return self.deductions.get(section)
    
    def has_deduction(self, section: str) -> bool:
        """Check if deduction exists for section"""
        return section in self.deductions
    
    def is_calculation_valid(self) -> bool:
        """Check if tax calculation is valid and up-to-date"""
        return (self.calculated_tax is not None and 
                self.total_tax_liability is not None and
                self.calculated_at is not None)
    
    def get_effective_tax_rate(self) -> float:
        """Calculate effective tax rate as percentage"""
        if not self.gross_annual_salary.is_positive() or not self.total_tax_liability:
            return 0.0
        
        return float((self.total_tax_liability.amount / self.gross_annual_salary.amount) * 100)
    
    def get_tax_savings(self) -> Money:
        """Calculate tax savings from deductions"""
        if not self.regime.allows_deductions():
            return Money.zero()
        
        # This is a simplified calculation
        # In reality, you'd need to calculate tax without deductions and compare
        total_deductions = self.get_total_deductions()
        # Assuming average tax rate of 20% for savings calculation
        return total_deductions.multiply(Decimal('0.20'))
    
    def _calculate_taxable_income(self) -> Money:
        """Calculate taxable income after deductions"""
        taxable = self.gross_annual_salary
        
        # Apply standard deduction
        standard_deduction = Money.from_float(self.regime.get_standard_deduction_limit())
        taxable = taxable.subtract(standard_deduction)
        
        # Apply other deductions if allowed
        if self.regime.allows_deductions():
            total_deductions = self.get_total_deductions()
            taxable = taxable.subtract(total_deductions)
        
        return taxable
    
    def _calculate_income_tax(self) -> Money:
        """Calculate income tax based on tax slabs"""
        if not self.taxable_income:
            return Money.zero()
        
        tax_slabs = self.regime.get_tax_slabs()
        total_tax = Money.zero()
        remaining_income = self.taxable_income.amount
        
        for slab in tax_slabs:
            if remaining_income <= 0:
                break
            
            slab_min = slab['min']
            slab_max = slab['max']
            slab_rate = slab['rate']
            
            if remaining_income <= slab_min:
                continue
            
            if slab_max is None:
                # Last slab (no upper limit)
                taxable_in_slab = remaining_income - slab_min
            else:
                taxable_in_slab = min(remaining_income, slab_max) - slab_min
            
            if taxable_in_slab > 0:
                slab_tax = Money(taxable_in_slab * (slab_rate / 100))
                total_tax = total_tax.add(slab_tax)
        
        return total_tax
    
    def _calculate_surcharge(self) -> Money:
        """Calculate surcharge based on income"""
        if not self.calculated_tax or not self.taxable_income:
            return Money.zero()
        
        surcharge_slabs = self.regime.get_surcharge_slabs()
        income_amount = self.taxable_income.amount
        
        for slab in surcharge_slabs:
            slab_min = slab['min']
            slab_max = slab['max']
            slab_rate = slab['rate']
            
            if slab_max is None:
                # Last slab
                if income_amount > slab_min:
                    return self.calculated_tax.multiply(slab_rate / 100)
            else:
                if slab_min < income_amount <= slab_max:
                    return self.calculated_tax.multiply(slab_rate / 100)
        
        return Money.zero()
    
    def _calculate_cess(self) -> Money:
        """Calculate health and education cess"""
        if not self.calculated_tax:
            return Money.zero()
        
        cess_rate = self.regime.get_cess_rate()
        tax_plus_surcharge = self.calculated_tax.add(self.surcharge_amount or Money.zero())
        return tax_plus_surcharge.multiply(cess_rate / 100)
    
    def _calculate_rebate_87a(self) -> Money:
        """Calculate rebate under section 87A"""
        if not self.regime.supports_rebate_87a() or not self.taxable_income:
            return Money.zero()
        
        rebate_limit = Money.from_float(self.regime.get_rebate_87a_limit())
        rebate_amount = Money.from_float(self.regime.get_rebate_87a_amount())
        
        if self.taxable_income.amount <= rebate_limit.amount:
            # Rebate is minimum of calculated tax and rebate amount
            if self.calculated_tax:
                return self.calculated_tax.min(rebate_amount)
        
        return Money.zero()
    
    def _calculate_total_tax_liability(self) -> Money:
        """Calculate total tax liability after all adjustments"""
        total = Money.zero()
        
        if self.calculated_tax:
            total = total.add(self.calculated_tax)
        
        if self.surcharge_amount:
            total = total.add(self.surcharge_amount)
        
        if self.cess_amount:
            total = total.add(self.cess_amount)
        
        if self.rebate_87a:
            total = total.subtract(self.rebate_87a)
        
        return total
    
    def _is_deduction_allowed(self, section: str) -> bool:
        """Check if deduction section is allowed for current regime"""
        allowed_sections = self.regime.get_allowed_deduction_sections()
        return section in allowed_sections
    
    def _validate_deduction_limit(self, section: str, amount: Money):
        """Validate deduction amount against section limits"""
        # This would contain business rules for each section's limits
        # For example, Section 80C has a limit of Rs. 1.5 lakhs
        
        if section == "80C" and amount.amount > Decimal('150000'):
            raise ValueError("Section 80C deduction cannot exceed Rs. 1,50,000")
        
        if section == "80D":
            # Different limits for different age groups
            # This would need employee age information
            pass
    
    def _validate_deductions_for_regime(self):
        """Remove deductions not allowed in current regime"""
        allowed_sections = self.regime.get_allowed_deduction_sections()
        sections_to_remove = []
        
        for section in self.deductions.keys():
            if section not in allowed_sections:
                sections_to_remove.append(section)
        
        for section in sections_to_remove:
            self.remove_deduction(section)
    
    def _clear_calculated_values(self):
        """Clear calculated values when inputs change"""
        self.taxable_income = None
        self.calculated_tax = None
        self.cess_amount = None
        self.surcharge_amount = None
        self.total_tax_liability = None
        self.rebate_87a = Money.zero()
        self.calculated_at = None
    
    def _validate_taxation_data(self):
        """Validate taxation data consistency"""
        
        if not self.tax_year:
            raise ValueError("Tax year is required")
        
        if not self.gross_annual_salary.is_positive():
            raise ValueError("Gross annual salary must be positive")
        
        # Validate tax year format (e.g., "2023-24")
        if not self._is_valid_tax_year_format(self.tax_year):
            raise ValueError("Invalid tax year format. Expected format: YYYY-YY")
    
    def _is_valid_tax_year_format(self, tax_year: str) -> bool:
        """Validate tax year format"""
        import re
        pattern = r'^\d{4}-\d{2}$'
        return bool(re.match(pattern, tax_year))
    
    def get_domain_events(self) -> List:
        """Get list of domain events"""
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        """Clear domain events after processing"""
        self._domain_events.clear()
    
    def __str__(self) -> str:
        """String representation"""
        return f"Taxation({self.employee_id}, {self.tax_year}, {self.regime})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Taxation(employee_id={self.employee_id}, tax_year='{self.tax_year}', regime={self.regime})" 