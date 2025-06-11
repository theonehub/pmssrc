"""
Retirement Benefits Entity
Represents various retirement benefits and their tax treatment
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.domain.value_objects.money import Money


@dataclass
class RetirementBenefits:
    """Retirement benefits entity containing various retirement benefits."""
    
    # Gratuity
    gratuity_amount: Money = Money.zero()
    years_of_service: int = 0
    is_government_employee: bool = False
    
    # Leave encashment
    leave_encashment_amount: Money = Money.zero()
    leave_balance: int = 0
    
    # Pension
    pension_amount: Money = Money.zero()
    is_commuted_pension: bool = False
    commutation_percentage: Decimal = Decimal('0')
    
    # VRS compensation
    vrs_compensation: Money = Money.zero()
    
    # Other benefits
    other_retirement_benefits: Money = Money.zero()
    
    def get_gratuity_exemption(self) -> Money:
        """
        Calculate gratuity exemption.
        
        For government employees:
        - Entire gratuity is exempt
        
        For other employees:
        - Minimum of:
          1. ₹20 lakh
          2. Last drawn salary × years of service × 15/26
          3. Actual gratuity received
        """
        if self.is_government_employee:
            return self.gratuity_amount
        
        if self.years_of_service < 5:
            return Money.zero()
        
        # Calculate based on last drawn salary
        # Note: Last drawn salary should be passed as parameter
        # For now using a placeholder
        last_drawn_salary = Money(Decimal('50000'))  # Placeholder
        
        calculated_amount = (
            last_drawn_salary
            .multiply(Decimal(str(self.years_of_service)))
            .multiply(Decimal('15'))
            .divide(Decimal('26'))
        )
        
        # Take minimum of all three
        exemption = min(
            Decimal('2000000'),  # ₹20 lakh
            calculated_amount.amount,
            self.gratuity_amount.amount
        )
        
        return Money(Decimal(str(exemption)))
    
    def get_leave_encashment_exemption(self) -> Money:
        """
        Calculate leave encashment exemption.
        
        For government employees:
        - Entire leave encashment is exempt
        
        For other employees:
        - Minimum of:
          1. ₹3 lakh
          2. Last drawn salary × leave balance / 30
          3. Actual leave encashment received
        """
        if self.is_government_employee:
            return self.leave_encashment_amount
        
        if self.years_of_service < 5:
            return Money.zero()
        
        # Calculate based on last drawn salary
        # Note: Last drawn salary should be passed as parameter
        # For now using a placeholder
        last_drawn_salary = Money(Decimal('50000'))  # Placeholder
        
        calculated_amount = (
            last_drawn_salary
            .multiply(Decimal(str(self.leave_balance)))
            .divide(Decimal('30'))
        )
        
        # Take minimum of all three
        exemption = min(
            Decimal('300000'),  # ₹3 lakh
            calculated_amount.amount,
            self.leave_encashment_amount.amount
        )
        
        return Money(Decimal(str(exemption)))
    
    def get_pension_exemption(self) -> Money:
        """
        Calculate pension exemption.
        
        For uncommuted pension:
        - Fully taxable
        
        For commuted pension:
        - Government employees: Fully exempt
        - Other employees: 1/3 of commuted value is exempt
        """
        if not self.is_commuted_pension:
            return Money.zero()
        
        if self.is_government_employee:
            return self.pension_amount
        
        # For other employees, 1/3 of commuted value is exempt
        return self.pension_amount.divide(3)
    
    def get_vrs_exemption(self) -> Money:
        """
        Calculate VRS compensation exemption.
        
        Exemption is available up to ₹5 lakh.
        """
        if self.vrs_compensation.is_less_than(Money(Decimal('500000'))):
            return self.vrs_compensation
        else:
            return Money(Decimal('500000'))
    
    def get_total_exemptions(self) -> Money:
        """Get total exemptions from retirement benefits."""
        return (
            self.get_gratuity_exemption()
            .add(self.get_leave_encashment_exemption())
            .add(self.get_pension_exemption())
            .add(self.get_vrs_exemption())
        )
    
    def get_taxable_retirement_benefits(self) -> Money:
        """
        Calculate taxable retirement benefits.
        
        Taxable amount = Total benefits - Total exemptions
        """
        total_benefits = (
            self.gratuity_amount
            .add(self.leave_encashment_amount)
            .add(self.pension_amount)
            .add(self.vrs_compensation)
            .add(self.other_retirement_benefits)
        )
        
        return total_benefits.subtract(self.get_total_exemptions())
    
    def get_benefit_type_description(self) -> str:
        """Get human-readable benefit type description."""
        if self.is_government_employee:
            return "Government Employee Benefits"
        else:
            return "Private Employee Benefits"
    
    def get_pension_type_description(self) -> str:
        """Get human-readable pension type description."""
        if self.is_commuted_pension:
            return f"Commuted Pension ({self.commutation_percentage}% commuted)"
        else:
            return "Uncommuted Pension" 