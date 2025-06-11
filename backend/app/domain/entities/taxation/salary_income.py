"""
Salary Income Entity
Represents salary components for tax calculation
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.domain.value_objects.money import Money


@dataclass
class SalaryIncome:
    """Salary income entity containing all salary components."""
    
    # Basic salary components
    basic_salary: Money
    dearness_allowance: Money
    house_rent_allowance: Money
    special_allowance: Money
    conveyance_allowance: Money
    medical_allowance: Money
    
    # Additional components
    bonus: Money = Money.zero()
    commission: Money = Money.zero()
    overtime: Money = Money.zero()
    arrears: Money = Money.zero()
    gratuity: Money = Money.zero()
    leave_encashment: Money = Money.zero()
    other_allowances: Money = Money.zero()
    
    # Exemptions
    hra_exemption: Money = Money.zero()
    conveyance_exemption: Money = Money.zero()
    medical_exemption: Money = Money.zero()
    gratuity_exemption: Money = Money.zero()
    leave_encashment_exemption: Money = Money.zero()
    
    def get_total_salary(self) -> Money:
        """Get total salary including all components."""
        return (
            self.basic_salary
            .add(self.dearness_allowance)
            .add(self.house_rent_allowance)
            .add(self.special_allowance)
            .add(self.conveyance_allowance)
            .add(self.medical_allowance)
            .add(self.bonus)
            .add(self.commission)
            .add(self.overtime)
            .add(self.arrears)
            .add(self.gratuity)
            .add(self.leave_encashment)
            .add(self.other_allowances)
        )
    
    def get_total_exemptions(self) -> Money:
        """Get total exemptions from salary."""
        return (
            self.hra_exemption
            .add(self.conveyance_exemption)
            .add(self.medical_exemption)
            .add(self.gratuity_exemption)
            .add(self.leave_encashment_exemption)
        )
    
    def get_taxable_salary(self) -> Money:
        """Get taxable salary after exemptions."""
        return self.get_total_salary().subtract(self.get_total_exemptions())
    
    def calculate_hra_exemption(self, 
                              rent_paid: Money,
                              metro_city: bool,
                              basic_salary: Optional[Money] = None) -> Money:
        """
        Calculate HRA exemption based on:
        1. Actual HRA received
        2. Rent paid minus 10% of basic salary
        3. 50% of basic salary (metro) or 40% (non-metro)
        
        Args:
            rent_paid: Monthly rent paid
            metro_city: Whether city is metro
            basic_salary: Basic salary (defaults to self.basic_salary)
            
        Returns:
            Money: HRA exemption amount
        """
        if basic_salary is None:
            basic_salary = self.basic_salary
        
        # Calculate 10% of basic salary
        basic_10_percent = basic_salary.percentage(Decimal('10'))
        
        # Calculate rent paid minus 10% of basic
        rent_minus_basic = rent_paid.subtract(basic_10_percent)
        if not rent_minus_basic.is_positive():
            rent_minus_basic = Money.zero()
        
        # Calculate 50% or 40% of basic
        if metro_city:
            basic_percentage = basic_salary.percentage(Decimal('50'))
        else:
            basic_percentage = basic_salary.percentage(Decimal('40'))
        
        # Take minimum of all three
        exemption = min(
            self.house_rent_allowance.amount,
            rent_minus_basic.amount,
            basic_percentage.amount
        )
        
        return Money(Decimal(str(exemption)))
    
    def calculate_conveyance_exemption(self) -> Money:
        """
        Calculate conveyance allowance exemption.
        Maximum ₹1,600 per month (₹19,200 per year) is exempt.
        """
        max_monthly = Money(Decimal('1600'))
        max_yearly = Money(Decimal('19200'))
        
        if self.conveyance_allowance.is_less_than(max_monthly):
            return self.conveyance_allowance
        else:
            return max_monthly
    
    def calculate_medical_exemption(self) -> Money:
        """
        Calculate medical allowance exemption.
        Maximum ₹15,000 per year is exempt.
        """
        max_yearly = Money(Decimal('15000'))
        
        if self.medical_allowance.is_less_than(max_yearly):
            return self.medical_allowance
        else:
            return max_yearly
    
    def calculate_gratuity_exemption(self, years_of_service: int) -> Money:
        """
        Calculate gratuity exemption.
        
        Args:
            years_of_service: Number of years of service
            
        Returns:
            Money: Exempt amount of gratuity
        """
        # For government employees, entire gratuity is exempt
        # For others, minimum of:
        # 1. ₹20 lakh
        # 2. Last drawn salary × years of service × 15/26
        # 3. Actual gratuity received
        
        if years_of_service < 5:
            return Money.zero()
        
        # Calculate based on last drawn salary
        last_drawn_salary = self.basic_salary.add(self.dearness_allowance)
        calculated_amount = (
            last_drawn_salary
            .multiply(Decimal(str(years_of_service)))
            .multiply(Decimal('15'))
            .divide(Decimal('26'))
        )
        
        # Take minimum of all three
        exemption = min(
            Decimal('2000000'),  # ₹20 lakh
            calculated_amount.amount,
            self.gratuity.amount
        )
        
        return Money(Decimal(str(exemption)))
    
    def calculate_leave_encashment_exemption(self, 
                                           years_of_service: int,
                                           leave_balance: int) -> Money:
        """
        Calculate leave encashment exemption.
        
        Args:
            years_of_service: Number of years of service
            leave_balance: Number of days of leave balance
            
        Returns:
            Money: Exempt amount of leave encashment
        """
        # For government employees, entire leave encashment is exempt
        # For others, minimum of:
        # 1. ₹3 lakh
        # 2. Last drawn salary × leave balance / 30
        # 3. Actual leave encashment received
        
        if years_of_service < 5:
            return Money.zero()
        
        # Calculate based on last drawn salary
        last_drawn_salary = self.basic_salary.add(self.dearness_allowance)
        calculated_amount = (
            last_drawn_salary
            .multiply(Decimal(str(leave_balance)))
            .divide(Decimal('30'))
        )
        
        # Take minimum of all three
        exemption = min(
            Decimal('300000'),  # ₹3 lakh
            calculated_amount.amount,
            self.leave_encashment.amount
        )
        
        return Money(Decimal(str(exemption))) 