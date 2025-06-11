"""
Retirement Benefits Entity
Domain entity for handling retirement benefits calculations
"""

from dataclasses import dataclass
from typing import Dict, Any
from decimal import Decimal
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType


@dataclass
class LeaveEncashment:
    """Leave encashment benefit calculation."""
    
    leave_encashment_amount: Money = Money.zero()
    average_monthly_salary: Money = Money.zero()
    leave_days_encashed: int = 0
    is_govt_employee: bool = False
    is_deceased: bool = False
    during_employment: bool = False
    
    def calculate_exemption(self) -> Money:
        """
        Calculate leave encashment exemption.
        
        Returns:
            Money: Exemption amount
        """
        if self.is_govt_employee or self.is_deceased:
            return self.leave_encashment_amount  # Fully exempt
        
        if self.during_employment:
            return Money.zero()  # No exemption during employment
        
        # On retirement/termination - minimum of 4 amounts
        actual_received = self.leave_encashment_amount
        ten_months_salary = self.average_monthly_salary.multiply(10)
        statutory_limit = Money.from_int(2500000)  # ₹25 lakh
        
        # Unexpired leave value calculation
        daily_salary = self.average_monthly_salary.divide(30)
        unexpired_leave_value = daily_salary.multiply(self.leave_days_encashed)
        
        # Find minimum of all four amounts
        min_amount = actual_received.min(ten_months_salary)
        min_amount = min_amount.min(statutory_limit)
        min_amount = min_amount.min(unexpired_leave_value)
        return min_amount
    
    def calculate_taxable_amount(self) -> Money:
        """
        Calculate taxable leave encashment amount.
        
        Returns:
            Money: Taxable amount
        """
        exemption = self.calculate_exemption()
        return self.leave_encashment_amount.subtract(exemption).max(Money.zero())


@dataclass
class Gratuity:
    """Gratuity benefit calculation."""
    
    gratuity_amount: Money = Money.zero()
    monthly_salary: Money = Money.zero()
    service_years: Decimal = Decimal('0')
    is_govt_employee: bool = False
    
    def calculate_exemption(self) -> Money:
        """
        Calculate gratuity exemption.
        
        Returns:
            Money: Exemption amount
        """
        if self.is_govt_employee:
            return self.gratuity_amount  # Fully exempt for government employees
        
        # Non-government employees - minimum of 3 amounts
        actual_received = self.gratuity_amount
        daily_salary = self.monthly_salary.divide(26)  # 26 working days
        salary_based_exemption = daily_salary.multiply(15).multiply(float(self.service_years))
        statutory_limit = Money.from_int(2000000)  # ₹20 lakh
        
        # Find minimum of all three amounts
        min_amount = actual_received.min(salary_based_exemption)
        min_amount = min_amount.min(statutory_limit)
        return min_amount
    
    def calculate_taxable_amount(self) -> Money:
        """
        Calculate taxable gratuity amount.
        
        Returns:
            Money: Taxable amount
        """
        exemption = self.calculate_exemption()
        return self.gratuity_amount.subtract(exemption).max(Money.zero())


@dataclass
class VRS:
    """Voluntary Retirement Scheme benefit calculation."""
    
    vrs_amount: Money = Money.zero()
    monthly_salary: Money = Money.zero()
    age: int = 25
    service_years: Decimal = Decimal('0')
    
    def is_eligible(self) -> bool:
        """
        Check VRS eligibility.
        
        Returns:
            bool: Eligibility status
        """
        return self.age >= 40 and self.service_years >= 10
    
    def calculate_vrs_value(self) -> Money:
        """
        Calculate VRS value as per formula.
        
        Returns:
            Money: Calculated VRS value
        """
        if not self.is_eligible():
            return Money.zero()
        
        single_day_salary = self.monthly_salary.divide(30)
        salary_45_days = single_day_salary.multiply(45)
        
        months_remaining = (60 - self.age) * 12
        salary_for_remaining_months = self.monthly_salary.multiply(months_remaining)
        
        salary_for_service = salary_45_days.multiply(float(self.service_years))
        
        return salary_for_remaining_months.min(salary_for_service)
    
    def calculate_exemption(self) -> Money:
        """
        Calculate VRS exemption (₹5 lakh).
        
        Returns:
            Money: Exemption amount
        """
        if not self.is_eligible():
            return Money.zero()
        
        exemption_limit = Money.from_int(500000)  # ₹5 lakh
        return self.vrs_amount.min(exemption_limit)
    
    def calculate_taxable_amount(self) -> Money:
        """
        Calculate taxable VRS amount.
        
        Returns:
            Money: Taxable amount
        """
        exemption = self.calculate_exemption()
        return self.vrs_amount.subtract(exemption).max(Money.zero())


@dataclass
class Pension:
    """Pension benefit calculation."""
    
    regular_pension: Money = Money.zero()
    commuted_pension: Money = Money.zero()
    total_pension: Money = Money.zero()
    is_govt_employee: bool = False
    gratuity_received: bool = False
    
    def calculate_commuted_pension_exemption(self) -> Money:
        """
        Calculate commuted pension exemption.
        
        Returns:
            Money: Exemption amount
        """
        if self.is_govt_employee:
            return self.commuted_pension  # Fully exempt for government employees
        
        # For non-government employees
        if self.gratuity_received:
            exemption_fraction = Decimal('1') / Decimal('3')  # 1/3rd
        else:
            exemption_fraction = Decimal('1') / Decimal('2')  # 1/2
        
        exemption_limit = self.total_pension.percentage(float(exemption_fraction * 100))
        return self.commuted_pension.min(exemption_limit)
    
    def calculate_taxable_pension(self) -> Money:
        """
        Calculate taxable pension amount.
        
        Returns:
            Money: Taxable pension
        """
        # Regular pension is fully taxable
        commuted_exemption = self.calculate_commuted_pension_exemption()
        taxable_commuted = self.commuted_pension.subtract(commuted_exemption)
        
        return self.regular_pension.add(taxable_commuted)


@dataclass
class RetrenchmentCompensation:
    """Retrenchment compensation calculation."""
    
    retrenchment_amount: Money = Money.zero()
    monthly_salary: Money = Money.zero()
    service_years: Decimal = Decimal('0')
    
    def calculate_completed_years(self) -> int:
        """
        Calculate completed years of service for exemption.
        
        Returns:
            int: Completed years
        """
        completed_years = int(self.service_years)
        remaining_days = (self.service_years - completed_years) * Decimal('365.25')
        
        # If remaining days > 6 months (182.625 days), count as additional year
        if remaining_days > Decimal('182.625'):
            completed_years += 1
        
        return completed_years
    
    def calculate_exemption(self) -> Money:
        """
        Calculate retrenchment compensation exemption.
        
        Returns:
            Money: Exemption amount
        """
        # Minimum of 3 amounts
        actual_received = self.retrenchment_amount
        statutory_limit = Money.from_int(500000)  # ₹5 lakh
        
        daily_salary = self.monthly_salary.divide(30)
        completed_years = self.calculate_completed_years()
        salary_based_exemption = daily_salary.multiply(15).multiply(completed_years)
        
        # Find minimum of all three amounts
        min_amount = actual_received.min(salary_based_exemption)
        min_amount = min_amount.min(statutory_limit)
        return min_amount
    
    def calculate_taxable_amount(self) -> Money:
        """
        Calculate taxable retrenchment compensation.
        
        Returns:
            Money: Taxable amount
        """
        exemption = self.calculate_exemption()
        return self.retrenchment_amount.subtract(exemption).max(Money.zero())


@dataclass
class RetirementBenefits:
    """Comprehensive retirement benefits entity."""
    
    leave_encashment: LeaveEncashment = None
    gratuity: Gratuity = None
    vrs: VRS = None
    pension: Pension = None
    retrenchment_compensation: RetrenchmentCompensation = None
    
    def __post_init__(self):
        """Initialize default objects if not provided."""
        if self.leave_encashment is None:
            self.leave_encashment = LeaveEncashment()
        if self.gratuity is None:
            self.gratuity = Gratuity()
        if self.vrs is None:
            self.vrs = VRS()
        if self.pension is None:
            self.pension = Pension()
        if self.retrenchment_compensation is None:
            self.retrenchment_compensation = RetrenchmentCompensation()
    
    def calculate_total_retirement_income(self, regime: TaxRegime) -> Money:
        """
        Calculate total taxable retirement income.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Total taxable retirement income
        """
        total_income = Money.zero()
        
        # Add taxable amounts from each benefit
        total_income = total_income.add(self.leave_encashment.calculate_taxable_amount())
        total_income = total_income.add(self.gratuity.calculate_taxable_amount())
        total_income = total_income.add(self.vrs.calculate_taxable_amount())
        total_income = total_income.add(self.pension.calculate_taxable_pension())
        total_income = total_income.add(self.retrenchment_compensation.calculate_taxable_amount())
        
        return total_income
    
    def get_retirement_benefits_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """
        Get detailed breakdown of retirement benefits.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Complete retirement benefits breakdown
        """
        return {
            "regime": regime.regime_type.value,
            "leave_encashment": {
                "total_amount": self.leave_encashment.leave_encashment_amount.to_float(),
                "exemption": self.leave_encashment.calculate_exemption().to_float(),
                "taxable_amount": self.leave_encashment.calculate_taxable_amount().to_float(),
                "is_govt_employee": self.leave_encashment.is_govt_employee,
                "during_employment": self.leave_encashment.during_employment
            },
            "gratuity": {
                "total_amount": self.gratuity.gratuity_amount.to_float(),
                "exemption": self.gratuity.calculate_exemption().to_float(),
                "taxable_amount": self.gratuity.calculate_taxable_amount().to_float(),
                "is_govt_employee": self.gratuity.is_govt_employee,
                "service_years": float(self.gratuity.service_years)
            },
            "vrs": {
                "total_amount": self.vrs.vrs_amount.to_float(),
                "eligible": self.vrs.is_eligible(),
                "calculated_vrs_value": self.vrs.calculate_vrs_value().to_float(),
                "exemption": self.vrs.calculate_exemption().to_float(),
                "taxable_amount": self.vrs.calculate_taxable_amount().to_float(),
                "age": self.vrs.age,
                "service_years": float(self.vrs.service_years)
            },
            "pension": {
                "regular_pension": self.pension.regular_pension.to_float(),
                "commuted_pension": self.pension.commuted_pension.to_float(),
                "commuted_exemption": self.pension.calculate_commuted_pension_exemption().to_float(),
                "total_taxable_pension": self.pension.calculate_taxable_pension().to_float(),
                "is_govt_employee": self.pension.is_govt_employee,
                "gratuity_received": self.pension.gratuity_received
            },
            "retrenchment_compensation": {
                "total_amount": self.retrenchment_compensation.retrenchment_amount.to_float(),
                "exemption": self.retrenchment_compensation.calculate_exemption().to_float(),
                "taxable_amount": self.retrenchment_compensation.calculate_taxable_amount().to_float(),
                "completed_years": self.retrenchment_compensation.calculate_completed_years(),
                "service_years": float(self.retrenchment_compensation.service_years)
            },
            "summary": {
                "total_retirement_income": self.calculate_total_retirement_income(regime).to_float(),
                "total_exemptions": (
                    self.leave_encashment.calculate_exemption()
                    .add(self.gratuity.calculate_exemption())
                    .add(self.vrs.calculate_exemption())
                    .add(self.pension.calculate_commuted_pension_exemption())
                    .add(self.retrenchment_compensation.calculate_exemption())
                ).to_float()
            }
        } 