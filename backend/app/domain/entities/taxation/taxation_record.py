"""
Taxation Record Entity
Main aggregate root for taxation domain
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import uuid4

from app.domain.value_objects.employee_id import EmployeeId
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_year import TaxYear
from app.domain.value_objects.tax_regime import TaxRegime
from app.domain.entities.taxation.salary_income import SalaryIncome
from app.domain.entities.taxation.deductions import TaxDeductions
from app.domain.entities.taxation.perquisites import Perquisites
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.retirement_benefits import RetirementBenefits
from app.domain.entities.taxation.other_income import OtherIncome
from app.domain.entities.taxation.payout import PayoutMonthlyProjection
from app.domain.services.taxation.tax_calculation_service import TaxCalculationService, TaxCalculationResult


@dataclass
class TaxationRecord:
    """
    Main taxation aggregate root.
    
    Represents a complete tax record for an employee for a specific tax year.
    Contains all income types, deductions, and calculation information.
    
    Enhanced to support comprehensive Indian taxation:
    - Salary income (simple and periodic)  
    - Perquisites (all 15+ types)
    - House property income (now under other_income)
    - Capital gains
    - Retirement benefits
    - Other income sources
    - Monthly payroll with LWP
    """
    
    # Identifiers
    employee_id: EmployeeId
    tax_year: TaxYear
    
    # Core data (required for backward compatibility)
    salary_income: SalaryIncome
    deductions: TaxDeductions
    regime: TaxRegime
    age: int
    
    # Optional components with default values
    is_government_employee: bool = False
    perquisites: Optional[Perquisites] = None
    retirement_benefits: Optional[RetirementBenefits] = None
    other_income: Optional[OtherIncome] = None
    
    # Comprehensive income components (optional for backward compatibility)
    organization_id: Optional[str] = None
    taxation_id: Optional[str] = None
    monthly_payroll: Optional[PayoutMonthlyProjection] = None
    
    # Calculated fields
    calculation_result: Optional[TaxCalculationResult] = None
    last_calculated_at: Optional[datetime] = None
    
    # Metadata
    is_final: bool = False
    submitted_at: Optional[datetime] = None
    
    # Audit fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    
    # Domain events (not persisted)
    _domain_events: List[Dict[str, Any]] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Validate the taxation record after initialization."""
        if self.age < 18 or self.age > 100:
            raise ValueError("Invalid age for taxation")
        if not self.taxation_id:
            self.taxation_id = str(uuid4())
    
    def calculate_tax(self, calculation_service: TaxCalculationService) -> TaxCalculationResult:
        """
        Calculate tax using domain service.
        
        Args:
            calculation_service: Tax calculation service
            
        Returns:
            TaxCalculationResult: Complete calculation result
        """
        
        # Calculate comprehensive gross income
        gross_income = self.calculate_comprehensive_gross_income()
        
        # Calculate total exemptions
        total_exemptions = self.calculate_comprehensive_exemptions()
        
        # Calculate total deductions
        total_deductions = self.deductions.calculate_total_deductions(self.regime)
        
        # Perform tax calculation
        self.calculation_result = calculation_service.calculate_income_tax(
            gross_income=gross_income,
            total_exemptions=total_exemptions,
            total_deductions=total_deductions,
            regime=self.regime,
            age=self.age
        )
        
        # Update metadata
        self.last_calculated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "TaxCalculated",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "tax_amount": self.calculation_result.total_tax_liability.to_float(),
            "regime": self.regime.regime_type.value,
            "calculated_at": self.last_calculated_at.isoformat()
        })
        
        return self.calculation_result
    
    def calculate_comprehensive_gross_income(self) -> Money:
        """
        Calculate comprehensive gross income from all sources.
        
        Returns:
            Money: Total gross income from all sources
        """
        total_income = Money.zero()
        
        # Salary income (core)
        total_income = total_income.add(self.salary_income.calculate_gross_salary())
        #taxable_salary = self.salary_income.calculate_taxable_salary(self.regime)

        # Other income (if any) - now includes house property income and capital gains
        if self.other_income:
            total_income = total_income.add(self.other_income.calculate_total_other_income_slab_rates(self.regime, self.age))
            adjustments_less = self.other_income.loss_from_house_property_income(self.regime)
            total_income = total_income.subtract(adjustments_less)
                    
        # Perquisites (if any)
        if self.perquisites:
            total_income = total_income.add(self.perquisites.calculate_total_perquisites(self.regime))
        
        # Retirement benefits (if any)
        if self.retirement_benefits:
            total_income = total_income.add(self.retirement_benefits.calculate_total_retirement_income(self.regime))
        
        
        return total_income
    
    def calculate_comprehensive_exemptions(self) -> Money:
        """
        Calculate comprehensive exemptions from all sources.
        
        Returns:
            Money: Total exemptions from all sources
        """
        total_exemptions = Money.zero()
        
        # Salary exemptions (core)
        total_exemptions = total_exemptions.add(self.salary_income.calculate_total_exemptions(self.regime, self.is_government_employee))
        
        # Capital gains exemptions
        if self.other_income and self.other_income.capital_gains_income:
            total_exemptions = total_exemptions.add(self.other_income.calculate_capital_gains_exemptions(self.regime))
        
        # Retirement benefits exemptions
        if self.retirement_benefits:
            total_exemptions = total_exemptions.add(self.retirement_benefits.calculate_total_retirement_income(self.regime))
        
        # Other income exemptions (interest exemptions)
        if self.other_income:
            total_exemptions = total_exemptions.add(self.other_income.calculate_interest_exemptions(self.regime, self.age))
        
        return total_exemptions
    
    def calculate_separate_capital_gains_tax(self) -> Money:
        """
        Calculate capital gains tax that's charged separately (not at slab rates).
        
        Returns:
            Money: Separate capital gains tax
        """
        if not self.other_income or not self.other_income.capital_gains_income:
            return Money.zero()
        
        return self.other_income.capital_gains_income.calculate_total_capital_gains_tax()
    
    def get_comprehensive_income_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of all income sources.
        
        Returns:
            Dict: Comprehensive income breakdown
        """
        breakdown = {
            "salary_income": {
                "gross_salary": self.salary_income.calculate_gross_salary().to_float(),
                "exemptions": self.salary_income.calculate_total_exemptions(self.regime, self.is_government_employee).to_float(),
                "breakdown": self.salary_income.get_salary_breakdown(self.regime, self.is_government_employee)
            }
        }
        
        if self.perquisites:
            breakdown["perquisites"] = {
                "total_value": self.perquisites.calculate_total_perquisites(self.regime).to_float(),
                "breakdown": self.perquisites.get_perquisites_breakdown(self.regime)
            }
        
        if self.other_income and self.other_income.capital_gains_income:
            breakdown["capital_gains_income"] = {
                "slab_rate_income": self.other_income.capital_gains_income.calculate_stcg_for_slab_rates().to_float(),
                "separate_tax": self.other_income.capital_gains_income.calculate_total_capital_gains_tax().to_float(),
                "breakdown": self.other_income.capital_gains_income.get_capital_gains_breakdown(self.regime)
            }
        
        if self.retirement_benefits:
            breakdown["retirement_benefits"] = {
                "taxable_amount": self.retirement_benefits.calculate_total_retirement_income(self.regime).to_float(),
                "exemptions": self.retirement_benefits.calculate_total_exemptions().to_float(),
                "breakdown": self.retirement_benefits.get_retirement_benefits_breakdown()
            }
        
        if self.other_income:
            breakdown["other_income"] = {
                "taxable_amount": self.other_income.calculate_total_other_income(self.regime, self.age).to_float(),
                "exemptions": self.other_income.calculate_interest_exemptions(self.regime, self.age).to_float(),
                "breakdown": self.other_income.get_other_income_breakdown(self.regime, self.age)
            }
        
        if self.monthly_payroll:
            breakdown["monthly_payroll"] = {
                "monthly_gross_salary": self.monthly_payroll.gross_salary,
                "monthly_net_salary": self.monthly_payroll.net_salary,
                "monthly_total_deductions": self.monthly_payroll.total_deductions,
                "monthly_tds": self.monthly_payroll.tds,
                "annual_gross_salary": self.monthly_payroll.annual_gross_salary,
                "annual_tax_liability": self.monthly_payroll.annual_tax_liability,
                "tax_regime": self.monthly_payroll.tax_regime,
                "effective_working_days": self.monthly_payroll.effective_working_days,
                "lwp_days": self.monthly_payroll.lwp_days,
                "status": self.monthly_payroll.status.value,
                "payout_details": {
                    "basic_salary": self.monthly_payroll.basic_salary,
                    "da": self.monthly_payroll.da,
                    "hra": self.monthly_payroll.hra,
                    "special_allowance": self.monthly_payroll.special_allowance,
                    "bonus": self.monthly_payroll.bonus,
                    "commission": self.monthly_payroll.commission,
                    "epf_employee": self.monthly_payroll.epf_employee,
                    "esi_employee": self.monthly_payroll.esi_employee,
                    "professional_tax": self.monthly_payroll.professional_tax,
                    "advance_deduction": self.monthly_payroll.advance_deduction,
                    "loan_deduction": self.monthly_payroll.loan_deduction,
                    "other_deductions": self.monthly_payroll.other_deductions
                }
            }
        
        return breakdown
    
    def update_perquisites(self, new_perquisites: Optional[Perquisites]) -> None:
        """
        Update perquisites information.
        
        Args:
            new_perquisites: New perquisites details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized tax record")
        
        old_value = Money.zero()
        if self.perquisites:
            old_value = self.perquisites.calculate_total_perquisites(self.regime)
        
        self.perquisites = new_perquisites
        
        new_value = Money.zero()
        if new_perquisites:
            new_value = new_perquisites.calculate_total_perquisites(self.regime)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "PerquisitesUpdated",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_perquisites_value": old_value.to_float(),
            "new_perquisites_value": new_value.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_house_property_income(self, new_house_property: Optional[HousePropertyIncome]) -> None:
        """
        Update house property income information.
        
        Args:
            new_house_property: New house property income details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized tax record")
        
        old_income = Money.zero()
        if self.other_income and self.other_income.house_property_income:
            old_income = self.other_income.house_property_income.calculate_net_income_from_house_property(self.regime)
        
        # Ensure other_income exists
        if not self.other_income:
            from app.domain.entities.taxation.other_income import OtherIncome
            self.other_income = OtherIncome()
        
        self.other_income.house_property_income = new_house_property
        
        new_income = Money.zero()
        if new_house_property:
            new_income = new_house_property.calculate_net_income_from_house_property(self.regime)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "HousePropertyIncomeUpdated",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_house_property_income": old_income.to_float(),
            "new_house_property_income": new_income.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_retirement_benefits(self, new_retirement_benefits: Optional[RetirementBenefits]) -> None:
        """
        Update retirement benefits information.
        
        Args:
            new_retirement_benefits: New retirement benefits details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized tax record")
        
        old_benefits = Money.zero()
        if self.retirement_benefits:
            old_benefits = self.retirement_benefits.calculate_total_retirement_income(self.regime)
        
        self.retirement_benefits = new_retirement_benefits
        
        new_benefits = Money.zero()
        if new_retirement_benefits:
            new_benefits = new_retirement_benefits.calculate_total_retirement_income(self.regime)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "RetirementBenefitsUpdated",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_retirement_benefits": old_benefits.to_float(),
            "new_retirement_benefits": new_benefits.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_other_income(self, new_other_income: Optional[OtherIncome]) -> None:
        """
        Update other income information.
        
        Args:
            new_other_income: New other income details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized tax record")
        
        old_income = Money.zero()
        if self.other_income:
            old_income = self.other_income.calculate_total_other_income(self.regime, self.age)
        
        self.other_income = new_other_income
        
        new_income = Money.zero()
        if new_other_income:
            new_income = new_other_income.calculate_total_other_income(self.regime, self.age)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "OtherIncomeUpdated",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_other_income": old_income.to_float(),
            "new_other_income": new_income.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_monthly_payroll(self, new_monthly_payroll: Optional[PayoutMonthlyProjection]) -> None:
        """
        Update monthly payroll information.
        
        Args:
            new_monthly_payroll: New monthly payroll details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized tax record")
        
        old_payroll = 0.0
        if self.monthly_payroll:
            old_payroll = self.monthly_payroll.annual_gross_salary
        
        self.monthly_payroll = new_monthly_payroll
        
        new_payroll = 0.0
        if new_monthly_payroll:
            new_payroll = new_monthly_payroll.annual_gross_salary
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "MonthlyPayrollUpdated",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_payroll_amount": old_payroll,
            "new_payroll_amount": new_payroll,
            "updated_at": self.updated_at.isoformat()
        })
    
    def has_comprehensive_income(self) -> bool:
        """
        Check if the record has any comprehensive income components beyond basic salary.
        
        Returns:
            bool: True if has any comprehensive income components
        """
        return any([
            self.perquisites is not None,
            self.other_income is not None and (
                self.other_income.house_property_income is not None or
                not self.other_income.dividend_income.is_zero() or
                not self.other_income.business_professional_income.is_zero() or
                not self.other_income.other_miscellaneous_income.is_zero() or
                not self.other_income.gifts_received.is_zero()
            ),
            self.other_income and self.other_income.capital_gains_income is not None,
            self.retirement_benefits is not None,
            self.monthly_payroll is not None
        ])
    
    def update_salary(self, new_salary: SalaryIncome) -> None:
        """
        Update salary information.
        
        Args:
            new_salary: New salary income details
        """
        if self.is_final:
            raise ValueError("Cannot update finalized tax record")
        
        old_gross = self.salary_income.calculate_gross_salary()
        self.salary_income = new_salary
        new_gross = new_salary.calculate_gross_salary()
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "SalaryUpdated",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_gross_salary": old_gross.to_float(),
            "new_gross_salary": new_gross.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_deductions(self, new_deductions: TaxDeductions) -> None:
        """
        Update deduction information.
        
        Args:
            new_deductions: New deduction details
        """
        if self.is_final:
            raise ValueError("Cannot update finalized tax record")
        
        old_deductions = self.deductions.calculate_total_deductions(self.regime)
        self.deductions = new_deductions
        new_deductions_total = new_deductions.calculate_total_deductions(self.regime)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "DeductionsUpdated",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_deductions": old_deductions.to_float(),
            "new_deductions": new_deductions_total.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def change_regime(self, new_regime: TaxRegime) -> None:
        """
        Change tax regime.
        
        Args:
            new_regime: New tax regime
        """
        if self.is_final:
            raise ValueError("Cannot update finalized tax record")
        
        old_regime = self.regime
        self.regime = new_regime
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "RegimeChanged",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_regime": old_regime.regime_type.value,
            "new_regime": new_regime.regime_type.value,
            "updated_at": self.updated_at.isoformat()
        })
    
    def finalize_record(self) -> None:
        """
        Finalize the tax record (no further changes allowed).
        """
        if not self.is_calculation_valid():
            raise ValueError("Cannot finalize record without valid calculation")
        
        self.is_final = True
        self.submitted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "TaxRecordFinalized",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "total_tax": self.calculation_result.total_tax_liability.to_float(),
            "finalized_at": self.submitted_at.isoformat()
        })
    
    def reopen_record(self) -> None:
        """
        Reopen a finalized record for modifications.
        """
        if not self.is_final:
            return  # Already open
        
        self.is_final = False
        self.submitted_at = None
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "TaxRecordReopened",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "reopened_at": self.updated_at.isoformat()
        })
    
    def _invalidate_calculation(self) -> None:
        """Invalidate current calculation and update metadata."""
        self.calculation_result = None
        self.last_calculated_at = None
        self.updated_at = datetime.utcnow()
        self.version += 1
    
    def _add_domain_event(self, event: Dict[str, Any]) -> None:
        """Add a domain event."""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[Dict[str, Any]]:
        """Get all domain events."""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear domain events after processing."""
        self._domain_events.clear()
    
    def is_calculation_valid(self) -> bool:
        """
        Check if current calculation is valid.
        
        Returns:
            bool: True if calculation is current and valid
        """
        return (self.calculation_result is not None and 
                self.last_calculated_at is not None and
                self.last_calculated_at >= self.updated_at)
    
    def get_tax_summary(self) -> Dict[str, Any]:
        """
        Get tax summary for display.
        
        Returns:
            Dict: Tax summary information
        """
        if not self.is_calculation_valid():
            return {
                "status": "calculation_required",
                "taxation_id": self.taxation_id,
                "employee_id": str(self.employee_id),
                "tax_year": str(self.tax_year),
                "regime": self.regime.regime_type.value,
                "is_final": self.is_final
            }
        
        return {
            "status": "calculated",
            "taxation_id": self.taxation_id,
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "regime": self.regime.regime_type.value,
            "is_final": self.is_final,
            "gross_income": self.calculation_result.gross_income.to_float(),
            "taxable_income": self.calculation_result.taxable_income.to_float(),
            "total_tax_liability": self.calculation_result.total_tax_liability.to_float(),
            "monthly_tax": self.calculation_result.monthly_tax_liability.to_float(),
            "effective_tax_rate": f"{self.calculation_result.effective_tax_rate:.2f}%",
            "last_calculated": self.last_calculated_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None
        }
    
    def get_detailed_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed tax breakdown.
        
        Returns:
            Dict: Complete tax calculation breakdown
        """
        if not self.is_calculation_valid():
            raise ValueError("No valid calculation available")
        
        result = {
            "taxation_record": {
                "id": self.taxation_id,
                "employee_id": str(self.employee_id),
                "organization_id": self.organization_id,
                "tax_year": str(self.tax_year),
                "age": self.age,
                "regime": self.regime.regime_type.value,
                "is_final": self.is_final,
                "last_calculated": self.last_calculated_at.isoformat(),
                "has_comprehensive_income": self.has_comprehensive_income()
            },
            "income_breakdown": self.get_comprehensive_income_breakdown(),
            "deduction_breakdown": self.deductions.get_deduction_breakdown(self.regime),
            "tax_calculation": self.calculation_result.calculation_breakdown,
            "validation_warnings": self._get_validation_warnings()
        }
        
        # Add separate capital gains tax if applicable
        if self.other_income and self.other_income.capital_gains_income:
            result["separate_capital_gains_tax"] = self.calculate_separate_capital_gains_tax().to_float()
        
        return result
    
    def _get_validation_warnings(self) -> List[str]:
        """Get validation warnings for the tax record."""
        warnings = []
        
        # HRA validation warnings
        hra_warnings = self.salary_income.validate_hra_details()
        warnings.extend(hra_warnings.values())
        
        # Deduction warnings
        if self.regime.allows_deductions():
            # Check if deductions are underutilized
            total_deductions = self.deductions.calculate_total_deductions(self.regime)
            if total_deductions.is_less_than(Money.from_int(100000)):  # Less than 1 lakh
                warnings.append("Consider maximizing tax-saving investments under Section 80C")
            
            # 80D warnings
            current_80d = self.deductions.section_80d.calculate_eligible_deduction(self.regime)
            if current_80d.is_zero():
                warnings.append("Consider health insurance for additional tax savings under Section 80D")
        
        # Age-based warnings
        if self.age >= 60 and self.regime.regime_type.value == "new":
            warnings.append("Senior citizens may benefit more from the old tax regime")
        
        return warnings
    
    def can_switch_regime(self) -> bool:
        """
        Check if regime can be switched.
        
        Returns:
            bool: True if regime switch is allowed
        """
        return not self.is_final
    
    def get_regime_switch_impact(self, calculation_service: TaxCalculationService) -> Dict[str, Any]:
        """
        Calculate impact of switching tax regime.
        
        Args:
            calculation_service: Tax calculation service
            
        Returns:
            Dict: Impact analysis of regime switch
        """
        from app.domain.services.tax_calculation_service import RegimeComparisonService
        
        # Create comparison service
        comparison_service = RegimeComparisonService(calculation_service)
        
        # Get comparison
        gross_income = self.salary_income.calculate_gross_salary()
        total_exemptions = self.salary_income.calculate_total_exemptions(self.regime, self.is_government_employee)
        total_deductions = self.deductions.calculate_total_deductions(TaxRegime.old_regime())
        
        comparison = comparison_service.compare_regimes(
            gross_income, total_exemptions, total_deductions, self.age
        )
        
        return {
            "current_regime": self.regime.regime_type.value,
            "comparison": comparison,
            "can_switch": self.can_switch_regime()
        }
    
    # Backward compatibility property
    @property
    def house_property_income(self) -> Optional[HousePropertyIncome]:
        """Backward compatibility: Get house property income from other_income."""
        if self.other_income:
            return self.other_income.house_property_income
        return None
    
    @property
    def capital_gains_income(self):
        """Backward compatibility: Get capital gains income from other_income."""
        if self.other_income:
            return self.other_income.capital_gains_income
        return None

@dataclass
class SalaryPackageRecord:
    """
    Main salary package aggregate root.
    
    Represents a complete salary components, values provided for a month, which can be used to calculate the tax for the month.
    Contains all income types, deductions, and calculation information.
    
    Enhanced to support comprehensive Indian taxation:
    - Salary income (simple and periodic)  
    - Perquisites (all 15+ types)
    - House property income (now under other_income)
    - Capital gains
    - Retirement benefits
    - Other income sources
    - Monthly payroll with LWP
    """
    
    # Identifiers
    employee_id: EmployeeId
    tax_year: TaxYear
    age: int
    regime: TaxRegime
    
    salary_incomes: List[SalaryIncome]
    deductions: TaxDeductions
    
    # Optional components
    is_government_employee: bool = False
    perquisites: Optional[Perquisites] = None
    retirement_benefits: Optional[RetirementBenefits] = None
    other_income: Optional[OtherIncome] = None
    
    # Identifiers
    salary_package_id: Optional[str] = None
    organization_id: Optional[str] = None
    
    # Calculated fields
    calculation_result: Optional[TaxCalculationResult] = None
    last_calculated_at: Optional[datetime] = None
    
    # Metadata
    is_final: bool = False
    submitted_at: Optional[datetime] = None
    
    # Audit fields
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    
    # Domain events (not persisted)
    _domain_events: List[Dict[str, Any]] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Validate the salary package record after initialization."""
        if self.age < 18 or self.age > 100:
            raise ValueError("Invalid age for taxation")
        if not self.salary_incomes:
            raise ValueError("At least one salary income is required")
        if not self.salary_package_id:
            self.salary_package_id = str(uuid4())
    
    def add_salary_income(self, salary_income: SalaryIncome) -> None:
        """
        Add a new salary income to the list.
        
        Args:
            salary_income: New salary income to add
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        self.salary_incomes.append(salary_income)
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "SalaryIncomeAdded",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "new_salary_gross": salary_income.calculate_gross_salary().to_float(),
            "total_salary_incomes": len(self.salary_incomes),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_latest_salary_income(self, new_salary_income: SalaryIncome) -> None:
        """
        Update the latest salary income in the list.
        
        Args:
            new_salary_income: New salary income to replace the latest one
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        if not self.salary_incomes:
            raise ValueError("No salary incomes to update")
        
        old_gross = self.salary_incomes[-1].calculate_gross_salary()
        self.salary_incomes[-1] = new_salary_income
        new_gross = new_salary_income.calculate_gross_salary()
        
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "LatestSalaryIncomeUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_gross_salary": old_gross.to_float(),
            "new_gross_salary": new_gross.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def get_latest_salary_income(self) -> SalaryIncome:
        """
        Get the latest salary income from the list.
        
        Returns:
            SalaryIncome: Latest salary income
        """
        if not self.salary_incomes:
            raise ValueError("No salary incomes available")
        return self.salary_incomes[-1]
    
    def get_salary_income_history(self) -> List[SalaryIncome]:
        """
        Get all salary incomes in chronological order.
        
        Returns:
            List[SalaryIncome]: List of all salary incomes
        """
        return self.salary_incomes.copy()
    
    def calculate_tax(self, calculation_service: TaxCalculationService) -> TaxCalculationResult:
        """
        Calculate tax using domain service.
        
        Args:
            calculation_service: Tax calculation service
            
        Returns:
            TaxCalculationResult: Complete calculation result
        """
        
        # Calculate comprehensive gross income
        gross_income = self.calculate_comprehensive_gross_income()
        
        # Calculate total exemptions
        total_exemptions = self.calculate_comprehensive_exemptions()
        
        # Calculate total deductions
        total_deductions = self.deductions.calculate_total_deductions(self.regime)
        
        # Perform tax calculation
        self.calculation_result = calculation_service.calculate_income_tax(
            gross_income=gross_income,
            total_exemptions=total_exemptions,
            total_deductions=total_deductions,
            regime=self.regime,
            age=self.age
        )
        
        # Update metadata
        self.last_calculated_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "TaxCalculated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "tax_amount": self.calculation_result.total_tax_liability.to_float(),
            "regime": self.regime.regime_type.value,
            "calculated_at": self.last_calculated_at.isoformat()
        })
        
        return self.calculation_result
    
    def calculate_comprehensive_gross_income(self) -> Money:
        """
        Calculate comprehensive gross income from all sources.
        
        Returns:
            Money: Total gross income from all sources
        """
        total_income = Money.zero()
        
        # Use the latest salary income for calculation
        latest_salary = self.get_latest_salary_income()
        total_income = total_income.add(latest_salary.calculate_gross_salary())

        # Other income (if any) - now includes house property income and capital gains
        if self.other_income:
            total_income = total_income.add(self.other_income.calculate_total_other_income_slab_rates(self.regime, self.age))
            adjustments_less = self.other_income.loss_from_house_property_income(self.regime)
            total_income = total_income.subtract(adjustments_less)
                    
        # Perquisites (if any)
        if self.perquisites:
            total_income = total_income.add(self.perquisites.calculate_total_perquisites(self.regime))
        
        # Retirement benefits (if any)
        if self.retirement_benefits:
            total_income = total_income.add(self.retirement_benefits.calculate_total_retirement_income(self.regime))
        
        return total_income
    
    def calculate_comprehensive_exemptions(self) -> Money:
        """
        Calculate comprehensive exemptions from all sources.
        
        Returns:
            Money: Total exemptions from all sources
        """
        total_exemptions = Money.zero()
        
        # Salary exemptions (core) - use latest salary income
        latest_salary = self.get_latest_salary_income()
        total_exemptions = total_exemptions.add(latest_salary.calculate_total_exemptions(self.regime, self.is_government_employee))
        
        # Capital gains exemptions
        if self.other_income and self.other_income.capital_gains_income:
            total_exemptions = total_exemptions.add(self.other_income.calculate_capital_gains_exemptions(self.regime))
        
        # Retirement benefits exemptions
        if self.retirement_benefits:
            total_exemptions = total_exemptions.add(self.retirement_benefits.calculate_total_retirement_income(self.regime))
        
        # Other income exemptions (interest exemptions)
        if self.other_income:
            total_exemptions = total_exemptions.add(self.other_income.calculate_interest_exemptions(self.regime, self.age))
        
        return total_exemptions
    
    def update_perquisites(self, new_perquisites: Optional[Perquisites]) -> None:
        """
        Update perquisites information.
        
        Args:
            new_perquisites: New perquisites details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        old_value = Money.zero()
        if self.perquisites:
            old_value = self.perquisites.calculate_total_perquisites(self.regime)
        
        self.perquisites = new_perquisites
        
        new_value = Money.zero()
        if new_perquisites:
            new_value = new_perquisites.calculate_total_perquisites(self.regime)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "PerquisitesUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_perquisites_value": old_value.to_float(),
            "new_perquisites_value": new_value.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_house_property_income(self, new_house_property: Optional[HousePropertyIncome]) -> None:
        """
        Update house property income information.
        
        Args:
            new_house_property: New house property income details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        old_income = Money.zero()
        if self.other_income and self.other_income.house_property_income:
            old_income = self.other_income.house_property_income.calculate_net_income_from_house_property(self.regime)
        
        # Ensure other_income exists
        if not self.other_income:
            from app.domain.entities.taxation.other_income import OtherIncome
            self.other_income = OtherIncome()
        
        self.other_income.house_property_income = new_house_property
        
        new_income = Money.zero()
        if new_house_property:
            new_income = new_house_property.calculate_net_income_from_house_property(self.regime)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "HousePropertyIncomeUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_house_property_income": old_income.to_float(),
            "new_house_property_income": new_income.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_retirement_benefits(self, new_retirement_benefits: Optional[RetirementBenefits]) -> None:
        """
        Update retirement benefits information.
        
        Args:
            new_retirement_benefits: New retirement benefits details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        old_benefits = Money.zero()
        if self.retirement_benefits:
            old_benefits = self.retirement_benefits.calculate_total_retirement_income(self.regime)
        
        self.retirement_benefits = new_retirement_benefits
        
        new_benefits = Money.zero()
        if new_retirement_benefits:
            new_benefits = new_retirement_benefits.calculate_total_retirement_income(self.regime)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "RetirementBenefitsUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_retirement_benefits": old_benefits.to_float(),
            "new_retirement_benefits": new_benefits.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_other_income(self, new_other_income: Optional[OtherIncome]) -> None:
        """
        Update other income information.
        
        Args:
            new_other_income: New other income details (can be None)
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        old_income = Money.zero()
        if self.other_income:
            old_income = self.other_income.calculate_total_other_income(self.regime, self.age)
        
        self.other_income = new_other_income
        
        new_income = Money.zero()
        if new_other_income:
            new_income = new_other_income.calculate_total_other_income(self.regime, self.age)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "OtherIncomeUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_other_income": old_income.to_float(),
            "new_other_income": new_income.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def update_deductions(self, new_deductions: TaxDeductions) -> None:
        """
        Update deduction information.
        
        Args:
            new_deductions: New deduction details
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        old_deductions = self.deductions.calculate_total_deductions(self.regime)
        self.deductions = new_deductions
        new_deductions_total = new_deductions.calculate_total_deductions(self.regime)
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "DeductionsUpdated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_deductions": old_deductions.to_float(),
            "new_deductions": new_deductions_total.to_float(),
            "updated_at": self.updated_at.isoformat()
        })
    
    def change_regime(self, new_regime: TaxRegime) -> None:
        """
        Change tax regime.
        
        Args:
            new_regime: New tax regime
        """
        if self.is_final:
            raise ValueError("Cannot update finalized salary package record")
        
        old_regime = self.regime
        self.regime = new_regime
        
        # Invalidate calculation
        self._invalidate_calculation()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "RegimeChanged",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "old_regime": old_regime.regime_type.value,
            "new_regime": new_regime.regime_type.value,
            "updated_at": self.updated_at.isoformat()
        })
    
    def finalize_record(self) -> None:
        """
        Finalize the salary package record (no further changes allowed).
        """
        if not self.is_calculation_valid():
            raise ValueError("Cannot finalize record without valid calculation")
        
        self.is_final = True
        self.submitted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "SalaryPackageRecordFinalized",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "total_tax": self.calculation_result.total_tax_liability.to_float(),
            "finalized_at": self.submitted_at.isoformat()
        })
    
    def reopen_record(self) -> None:
        """
        Reopen a finalized record for modifications.
        """
        if not self.is_final:
            return  # Already open
        
        self.is_final = False
        self.submitted_at = None
        self.updated_at = datetime.utcnow()
        
        # Raise domain event
        self._add_domain_event({
            "event_type": "SalaryPackageRecordReopened",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "reopened_at": self.updated_at.isoformat()
        })
    
    def _invalidate_calculation(self) -> None:
        """Invalidate current calculation and update metadata."""
        self.calculation_result = None
        self.last_calculated_at = None
        self.updated_at = datetime.utcnow()
        self.version += 1
    
    def _add_domain_event(self, event: Dict[str, Any]) -> None:
        """Add a domain event."""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List[Dict[str, Any]]:
        """Get all domain events."""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """Clear domain events after processing."""
        self._domain_events.clear()
    
    def is_calculation_valid(self) -> bool:
        """
        Check if current calculation is valid.
        
        Returns:
            bool: True if calculation is current and valid
        """
        return (self.calculation_result is not None and 
                self.last_calculated_at is not None and
                self.last_calculated_at >= self.updated_at)
    
    def get_tax_summary(self) -> Dict[str, Any]:
        """
        Get tax summary for display.
        
        Returns:
            Dict: Tax summary information
        """
        if not self.is_calculation_valid():
            return {
                "status": "calculation_required",
                "employee_id": str(self.employee_id),
                "tax_year": str(self.tax_year),
                "regime": self.regime.regime_type.value,
                "is_final": self.is_final,
                "salary_incomes_count": len(self.salary_incomes)
            }
        
        return {
            "status": "calculated",
            "employee_id": str(self.employee_id),
            "tax_year": str(self.tax_year),
            "regime": self.regime.regime_type.value,
            "is_final": self.is_final,
            "gross_income": self.calculation_result.gross_income.to_float(),
            "taxable_income": self.calculation_result.taxable_income.to_float(),
            "total_tax_liability": self.calculation_result.total_tax_liability.to_float(),
            "monthly_tax": self.calculation_result.monthly_tax_liability.to_float(),
            "effective_tax_rate": f"{self.calculation_result.effective_tax_rate:.2f}%",
            "last_calculated": self.last_calculated_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "salary_incomes_count": len(self.salary_incomes)
        }
    
    def get_detailed_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed tax breakdown.
        
        Returns:
            Dict: Complete tax calculation breakdown
        """
        if not self.is_calculation_valid():
            raise ValueError("No valid calculation available")
        
        result = {
            "salary_package_record": {
                "employee_id": str(self.employee_id),
                "tax_year": str(self.tax_year),
                "age": self.age,
                "regime": self.regime.regime_type.value,
                "is_final": self.is_final,
                "last_calculated": self.last_calculated_at.isoformat(),
                "salary_incomes_count": len(self.salary_incomes),
                "has_comprehensive_income": self.has_comprehensive_income()
            },
            "income_breakdown": self.get_comprehensive_income_breakdown(),
            "deduction_breakdown": self.deductions.get_deduction_breakdown(self.regime),
            "tax_calculation": self.calculation_result.calculation_breakdown,
            "validation_warnings": self._get_validation_warnings()
        }
        
        # Add separate capital gains tax if applicable
        if self.other_income and self.other_income.capital_gains_income:
            result["separate_capital_gains_tax"] = self.calculate_separate_capital_gains_tax().to_float()
        
        return result
    
    def has_comprehensive_income(self) -> bool:
        """
        Check if the record has any comprehensive income components beyond basic salary.
        
        Returns:
            bool: True if has any comprehensive income components
        """
        return any([
            self.perquisites is not None,
            self.other_income is not None and (
                self.other_income.house_property_income is not None or
                not self.other_income.dividend_income.is_zero() or
                not self.other_income.business_professional_income.is_zero() or
                not self.other_income.other_miscellaneous_income.is_zero() or
                not self.other_income.gifts_received.is_zero()
            ),
            self.other_income and self.other_income.capital_gains_income is not None,
            self.retirement_benefits is not None
        ])
    
    def calculate_separate_capital_gains_tax(self) -> Money:
        """
        Calculate capital gains tax that's charged separately (not at slab rates).
        
        Returns:
            Money: Separate capital gains tax
        """
        if not self.other_income or not self.other_income.capital_gains_income:
            return Money.zero()
        
        return self.other_income.capital_gains_income.calculate_total_capital_gains_tax()
    
    def get_comprehensive_income_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed breakdown of all income sources.
        
        Returns:
            Dict: Comprehensive income breakdown
        """
        latest_salary = self.get_latest_salary_income()
        
        breakdown = {
            "salary_income": {
                "gross_salary": latest_salary.calculate_gross_salary().to_float(),
                "exemptions": latest_salary.calculate_total_exemptions(self.regime, self.is_government_employee).to_float(),
                "breakdown": latest_salary.get_salary_breakdown(self.regime, self.is_government_employee),
                "salary_incomes_count": len(self.salary_incomes),
                "salary_history": [
                    {
                        "index": i,
                        "gross_salary": salary.calculate_gross_salary().to_float(),
                        "basic_salary": salary.basic_salary.to_float(),
                        "special_allowance": salary.special_allowance.to_float()
                    }
                    for i, salary in enumerate(self.salary_incomes)
                ]
            }
        }
        
        if self.perquisites:
            breakdown["perquisites"] = {
                "total_value": self.perquisites.calculate_total_perquisites(self.regime).to_float(),
                "breakdown": self.perquisites.get_perquisites_breakdown(self.regime)
            }
        
        if self.other_income and self.other_income.capital_gains_income:
            breakdown["capital_gains_income"] = {
                "slab_rate_income": self.other_income.capital_gains_income.calculate_stcg_for_slab_rates().to_float(),
                "separate_tax": self.other_income.capital_gains_income.calculate_total_capital_gains_tax().to_float(),
                "breakdown": self.other_income.capital_gains_income.get_capital_gains_breakdown(self.regime)
            }
        
        if self.retirement_benefits:
            breakdown["retirement_benefits"] = {
                "taxable_amount": self.retirement_benefits.calculate_total_retirement_income(self.regime).to_float(),
                "exemptions": self.retirement_benefits.calculate_total_exemptions().to_float(),
                "breakdown": self.retirement_benefits.get_retirement_benefits_breakdown()
            }
        
        if self.other_income:
            breakdown["other_income"] = {
                "taxable_amount": self.other_income.calculate_total_other_income(self.regime, self.age).to_float(),
                "exemptions": self.other_income.calculate_interest_exemptions(self.regime, self.age).to_float(),
                "breakdown": self.other_income.get_other_income_breakdown(self.regime, self.age)
            }
        
        return breakdown
    
    def _get_validation_warnings(self) -> List[str]:
        """Get validation warnings for the salary package record."""
        warnings = []
        
        # HRA validation warnings
        latest_salary = self.get_latest_salary_income()
        hra_warnings = latest_salary.validate_hra_details()
        warnings.extend(hra_warnings.values())
        
        # Deduction warnings
        if self.regime.allows_deductions():
            # Check if deductions are underutilized
            total_deductions = self.deductions.calculate_total_deductions(self.regime)
            if total_deductions.is_less_than(Money.from_int(100000)):  # Less than 1 lakh
                warnings.append("Consider maximizing tax-saving investments under Section 80C")
            
            # 80D warnings
            current_80d = self.deductions.section_80d.calculate_eligible_deduction(self.regime)
            if current_80d.is_zero():
                warnings.append("Consider health insurance for additional tax savings under Section 80D")
        
        # Age-based warnings
        if self.age >= 60 and self.regime.regime_type.value == "new":
            warnings.append("Senior citizens may benefit more from the old tax regime")
        
        # Salary history warnings
        if len(self.salary_incomes) > 1:
            warnings.append(f"Multiple salary revisions detected ({len(self.salary_incomes)} versions)")
        
        return warnings
    
    def can_switch_regime(self) -> bool:
        """
        Check if regime can be switched.
        
        Returns:
            bool: True if regime switch is allowed
        """
        return not self.is_final
    
    def get_regime_switch_impact(self, calculation_service: TaxCalculationService) -> Dict[str, Any]:
        """
        Calculate impact of switching tax regime.
        
        Args:
            calculation_service: Tax calculation service
            
        Returns:
            Dict: Impact analysis of regime switch
        """
        from app.domain.services.tax_calculation_service import RegimeComparisonService
        
        # Create comparison service
        comparison_service = RegimeComparisonService(calculation_service)
        
        # Get comparison
        latest_salary = self.get_latest_salary_income()
        gross_income = latest_salary.calculate_gross_salary()
        total_exemptions = latest_salary.calculate_total_exemptions(self.regime, self.is_government_employee)
        total_deductions = self.deductions.calculate_total_deductions(TaxRegime.old_regime())
        
        comparison = comparison_service.compare_regimes(
            gross_income, total_exemptions, total_deductions, self.age
        )
        
        return {
            "current_regime": self.regime.regime_type.value,
            "comparison": comparison,
            "can_switch": self.can_switch_regime()
        }
    
    def compute_monthly_tax(self, month: int, year: int) -> Money:
        """Compute monthly tax."""

        #Get latest salary income
        latest_salary_income = self.get_latest_salary_income()

        #Compute gross income from latest salary income
        gross_income = latest_salary_income.calculate_gross_salary()

        #TODO: Complete the logic to compute monthly tax

        return self.calculation_result.monthly_tax_liability


    # Backward compatibility properties
    @property
    def salary_income(self) -> SalaryIncome:
        """Backward compatibility: Get the latest salary income."""
        return self.get_latest_salary_income()
    
    @property
    def house_property_income(self) -> Optional[HousePropertyIncome]:
        """Backward compatibility: Get house property income from other_income."""
        if self.other_income:
            return self.other_income.house_property_income
        return None
    
    @property
    def capital_gains_income(self):
        """Backward compatibility: Get capital gains income from other_income."""
        if self.other_income:
            return self.other_income.capital_gains_income
        return None