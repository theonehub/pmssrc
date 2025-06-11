"""
Monthly Payroll Entity
Domain entity for handling monthly payroll calculations with LWP impact
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Any, List
from datetime import date

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.salary_income import SalaryIncome


@dataclass
class LWPDetails:
    """Leave Without Pay details for a month."""
    
    lwp_days: int = 0
    total_working_days: int = 30
    month: int = 1  # 1-12
    year: int = 2024
    
    def get_lwp_factor(self) -> Decimal:
        """
        Calculate the LWP factor (reduction factor for salary).
        
        Returns:
            Decimal: Factor between 0 and 1 representing salary reduction
        """
        if self.lwp_days <= 0 or self.total_working_days <= 0:
            return Decimal('1.0')  # No LWP
        
        if self.lwp_days >= self.total_working_days:
            return Decimal('0.0')  # Full month LWP
        
        return Decimal('1.0') - (Decimal(str(self.lwp_days)) / Decimal(str(self.total_working_days)))
    
    def get_paid_days(self) -> int:
        """Get number of paid days in the month."""
        return max(0, self.total_working_days - self.lwp_days)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "lwp_days": self.lwp_days,
            "total_working_days": self.total_working_days,
            "paid_days": self.get_paid_days(),
            "lwp_factor": float(self.get_lwp_factor()),
            "month": self.month,
            "year": self.year
        }


@dataclass
class MonthlyPayroll:
    """Monthly payroll calculation with LWP considerations."""
    
    base_salary_income: SalaryIncome
    lwp_details: LWPDetails
    
    def calculate_monthly_gross_without_lwp(self) -> Money:
        """
        Calculate monthly gross salary without LWP adjustment.
        
        Returns:
            Money: Base monthly gross salary
        """
        annual_gross = self.base_salary_income.calculate_gross_salary()
        return annual_gross.divide(12)
    
    def calculate_monthly_gross_with_lwp(self) -> Money:
        """
        Calculate monthly gross salary adjusted for LWP.
        
        Returns:
            Money: LWP-adjusted monthly gross salary
        """
        base_monthly = self.calculate_monthly_gross_without_lwp()
        lwp_factor = self.lwp_details.get_lwp_factor()
        return base_monthly.multiply(float(lwp_factor))
    
    def calculate_lwp_deduction(self) -> Money:
        """
        Calculate the amount deducted due to LWP.
        
        Returns:
            Money: LWP deduction amount
        """
        base_monthly = self.calculate_monthly_gross_without_lwp()
        adjusted_monthly = self.calculate_monthly_gross_with_lwp()
        return base_monthly.subtract(adjusted_monthly)
    
    def calculate_monthly_exemptions_with_lwp(self, regime: TaxRegime) -> Money:
        """
        Calculate monthly exemptions adjusted for LWP.
        Some exemptions like HRA need to be proportionally reduced.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: LWP-adjusted monthly exemptions
        """
        # Get annual exemptions and convert to monthly
        annual_exemptions = self.base_salary_income.calculate_total_exemptions(regime)
        base_monthly_exemptions = annual_exemptions.divide(12)
        
        # Adjust exemptions based on LWP factor
        lwp_factor = self.lwp_details.get_lwp_factor()
        
        # Some exemptions are proportional to salary (like HRA)
        # Others are fixed amounts (like medical allowance)
        
        # For simplicity, we'll apply LWP factor to all exemptions
        # In real scenarios, this might need more granular handling
        return base_monthly_exemptions.multiply(float(lwp_factor))
    
    def calculate_monthly_taxable_salary_with_lwp(self, regime: TaxRegime) -> Money:
        """
        Calculate monthly taxable salary after LWP adjustments.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Monthly taxable salary with LWP adjustments
        """
        monthly_gross = self.calculate_monthly_gross_with_lwp()
        monthly_exemptions = self.calculate_monthly_exemptions_with_lwp(regime)
        monthly_standard_deduction = regime.get_standard_deduction().divide(12)
        
        salary_after_exemptions = monthly_gross.subtract(monthly_exemptions)
        taxable_salary = salary_after_exemptions.subtract(monthly_standard_deduction)
        
        return taxable_salary if taxable_salary.is_positive() else Money.zero()
    
    def get_monthly_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """
        Get detailed monthly payroll breakdown with LWP impact.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Comprehensive monthly breakdown
        """
        base_monthly_gross = self.calculate_monthly_gross_without_lwp()
        adjusted_monthly_gross = self.calculate_monthly_gross_with_lwp()
        lwp_deduction = self.calculate_lwp_deduction()
        monthly_exemptions = self.calculate_monthly_exemptions_with_lwp(regime)
        monthly_taxable = self.calculate_monthly_taxable_salary_with_lwp(regime)
        
        return {
            "month_year": f"{self.lwp_details.month:02d}/{self.lwp_details.year}",
            "lwp_details": self.lwp_details.to_dict(),
            "salary_computation": {
                "base_monthly_gross": base_monthly_gross.to_float(),
                "lwp_deduction": lwp_deduction.to_float(),
                "adjusted_monthly_gross": adjusted_monthly_gross.to_float(),
                "monthly_exemptions": monthly_exemptions.to_float(),
                "monthly_standard_deduction": regime.get_standard_deduction().divide(12).to_float(),
                "monthly_taxable_salary": monthly_taxable.to_float()
            },
            "impact_analysis": {
                "salary_reduction_percentage": float((lwp_deduction.amount / base_monthly_gross.amount) * 100) if base_monthly_gross.is_positive() else 0,
                "effective_working_days": self.lwp_details.get_paid_days(),
                "lwp_impact_factor": float(self.lwp_details.get_lwp_factor())
            }
        }


@dataclass
class AnnualPayrollWithLWP:
    """Annual payroll calculation considering LWP across multiple months."""
    
    base_salary_income: SalaryIncome
    monthly_lwp_details: List[LWPDetails]  # 12 months of LWP data
    
    def __post_init__(self):
        """Validate that we have 12 months of data."""
        if len(self.monthly_lwp_details) != 12:
            raise ValueError("Must provide LWP details for all 12 months")
    
    def calculate_total_lwp_days(self) -> int:
        """Calculate total LWP days in the year."""
        return sum(lwp.lwp_days for lwp in self.monthly_lwp_details)
    
    def calculate_total_working_days(self) -> int:
        """Calculate total working days in the year."""
        return sum(lwp.total_working_days for lwp in self.monthly_lwp_details)
    
    def calculate_annual_gross_with_lwp(self) -> Money:
        """
        Calculate annual gross salary adjusted for LWP across all months.
        
        Returns:
            Money: LWP-adjusted annual gross salary
        """
        total_adjusted = Money.zero()
        base_annual = self.base_salary_income.calculate_gross_salary()
        base_monthly = base_annual.divide(12)
        
        for lwp_detail in self.monthly_lwp_details:
            monthly_factor = lwp_detail.get_lwp_factor()
            adjusted_monthly = base_monthly.multiply(float(monthly_factor))
            total_adjusted = total_adjusted.add(adjusted_monthly)
        
        return total_adjusted
    
    def calculate_annual_lwp_deduction(self) -> Money:
        """
        Calculate total annual deduction due to LWP.
        
        Returns:
            Money: Total LWP deduction for the year
        """
        base_annual = self.base_salary_income.calculate_gross_salary()
        adjusted_annual = self.calculate_annual_gross_with_lwp()
        
        # Handle case where base might be less than adjusted (shouldn't happen but safety check)
        if base_annual.is_greater_than(adjusted_annual):
            return base_annual.subtract(adjusted_annual)
        else:
            return Money.zero()  # No deduction if somehow adjusted is higher
    
    def calculate_annual_exemptions_with_lwp(self, regime: TaxRegime) -> Money:
        """
        Calculate annual exemptions adjusted for LWP.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: LWP-adjusted annual exemptions
        """
        total_adjusted_exemptions = Money.zero()
        base_annual_exemptions = self.base_salary_income.calculate_total_exemptions(regime)
        base_monthly_exemptions = base_annual_exemptions.divide(12)
        
        for lwp_detail in self.monthly_lwp_details:
            monthly_factor = lwp_detail.get_lwp_factor()
            adjusted_monthly_exemptions = base_monthly_exemptions.multiply(float(monthly_factor))
            total_adjusted_exemptions = total_adjusted_exemptions.add(adjusted_monthly_exemptions)
        
        return total_adjusted_exemptions
    
    def calculate_annual_taxable_with_lwp(self, regime: TaxRegime) -> Money:
        """
        Calculate annual taxable salary with LWP adjustments.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Annual taxable salary with LWP adjustments
        """
        annual_gross = self.calculate_annual_gross_with_lwp()
        annual_exemptions = self.calculate_annual_exemptions_with_lwp(regime)
        standard_deduction = regime.get_standard_deduction()
        
        salary_after_exemptions = annual_gross.subtract(annual_exemptions)
        taxable_salary = salary_after_exemptions.subtract(standard_deduction)
        
        return taxable_salary if taxable_salary.is_positive() else Money.zero()
    
    def get_monthly_payrolls(self) -> List[MonthlyPayroll]:
        """
        Get list of monthly payroll objects for each month.
        
        Returns:
            List[MonthlyPayroll]: Monthly payroll calculations
        """
        monthly_payrolls = []
        for lwp_detail in self.monthly_lwp_details:
            monthly_payroll = MonthlyPayroll(
                base_salary_income=self.base_salary_income,
                lwp_details=lwp_detail
            )
            monthly_payrolls.append(monthly_payroll)
        
        return monthly_payrolls
    
    def get_lwp_impact_analysis(self, regime: TaxRegime) -> Dict[str, Any]:
        """
        Get comprehensive LWP impact analysis.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Detailed LWP impact analysis
        """
        base_annual_gross = self.base_salary_income.calculate_gross_salary()
        adjusted_annual_gross = self.calculate_annual_gross_with_lwp()
        annual_lwp_deduction = self.calculate_annual_lwp_deduction()
        
        base_annual_taxable = self.base_salary_income.calculate_taxable_salary(regime)
        adjusted_annual_taxable = self.calculate_annual_taxable_with_lwp(regime)
        
        total_lwp_days = self.calculate_total_lwp_days()
        total_working_days = self.calculate_total_working_days()
        
        # Monthly breakdown
        monthly_breakdowns = []
        for i, lwp_detail in enumerate(self.monthly_lwp_details):
            monthly_payroll = MonthlyPayroll(self.base_salary_income, lwp_detail)
            monthly_breakdown = monthly_payroll.get_monthly_breakdown(regime)
            monthly_breakdowns.append(monthly_breakdown)
        
        return {
            "annual_summary": {
                "base_annual_gross": base_annual_gross.to_float(),
                "adjusted_annual_gross": adjusted_annual_gross.to_float(),
                "total_lwp_deduction": annual_lwp_deduction.to_float(),
                "base_annual_taxable": base_annual_taxable.to_float(),
                "adjusted_annual_taxable": adjusted_annual_taxable.to_float(),
                "taxable_income_reduction": base_annual_taxable.subtract(adjusted_annual_taxable).to_float()
            },
            "lwp_statistics": {
                "total_lwp_days": total_lwp_days,
                "total_working_days": total_working_days,
                "lwp_percentage": float((total_lwp_days / total_working_days) * 100) if total_working_days > 0 else 0,
                "average_monthly_lwp": total_lwp_days / 12,
                "months_with_lwp": len([lwp for lwp in self.monthly_lwp_details if lwp.lwp_days > 0])
            },
            "financial_impact": {
                "gross_salary_reduction_percentage": float((annual_lwp_deduction.amount / base_annual_gross.amount) * 100) if base_annual_gross.is_positive() else 0,
                "monthly_average_deduction": annual_lwp_deduction.divide(12).to_float(),
                "taxable_income_impact_percentage": float(((base_annual_taxable.subtract(adjusted_annual_taxable)).amount / base_annual_taxable.amount) * 100) if base_annual_taxable.is_positive() else 0
            },
            "monthly_breakdowns": monthly_breakdowns,
            "regime_used": regime.regime_type.value
        }
    
    def get_annual_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """
        Get detailed annual breakdown with LWP considerations.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Annual breakdown with LWP impact
        """
        base_breakdown = self.base_salary_income.get_salary_breakdown(regime)
        lwp_impact = self.get_lwp_impact_analysis(regime)
        
        return {
            "base_salary_breakdown": base_breakdown,
            "lwp_adjusted_calculations": {
                "annual_gross_with_lwp": self.calculate_annual_gross_with_lwp().to_float(),
                "annual_exemptions_with_lwp": self.calculate_annual_exemptions_with_lwp(regime).to_float(),
                "annual_taxable_with_lwp": self.calculate_annual_taxable_with_lwp(regime).to_float()
            },
            "lwp_impact_analysis": lwp_impact
        }