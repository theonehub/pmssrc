"""
Tax Deductions Entity
Represents various tax deductions under different sections
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.domain.value_objects.money import Money


@dataclass
class TaxDeductions:
    """Tax deductions entity containing all deduction components."""
    
    # Section 80C deductions (max ₹1.5 lakh)
    life_insurance_premium: Money = Money.zero()
    elss_investments: Money = Money.zero()
    public_provident_fund: Money = Money.zero()
    employee_provident_fund: Money = Money.zero()
    sukanya_samriddhi: Money = Money.zero()
    national_savings_certificate: Money = Money.zero()
    tax_saving_fixed_deposits: Money = Money.zero()
    principal_repayment_home_loan: Money = Money.zero()
    tuition_fees: Money = Money.zero()
    other_80c_deductions: Money = Money.zero()
    
    # Section 80D deductions (Health Insurance)
    health_insurance_self: Money = Money.zero()
    health_insurance_parents: Money = Money.zero()
    preventive_health_checkup: Money = Money.zero()
    
    # Section 80E deductions (Education Loan)
    education_loan_interest: Money = Money.zero()
    
    # Section 80G deductions (Donations)
    donations_80g: Money = Money.zero()
    
    # Section 80TTA deductions (Savings Account Interest)
    savings_account_interest: Money = Money.zero()
    
    # Section 80TTB deductions (Senior Citizen Interest)
    senior_citizen_interest: Money = Money.zero()
    
    # Section 80U deductions (Disability)
    disability_deduction: Money = Money.zero()
    
    # Section 80DDB deductions (Medical Treatment)
    medical_treatment_deduction: Money = Money.zero()
    
    # Section 80GGA deductions (Scientific Research)
    scientific_research_donation: Money = Money.zero()
    
    # Section 80GGC deductions (Political Donations)
    political_donation: Money = Money.zero()
    
    # Section 80IA deductions (Infrastructure)
    infrastructure_deduction: Money = Money.zero()
    
    # Section 80IB deductions (Industrial Undertakings)
    industrial_undertaking_deduction: Money = Money.zero()
    
    # Section 80IC deductions (Special Category States)
    special_category_state_deduction: Money = Money.zero()
    
    # Section 80ID deductions (Hotels)
    hotel_deduction: Money = Money.zero()
    
    # Section 80IE deductions (North Eastern States)
    north_eastern_state_deduction: Money = Money.zero()
    
    # Section 80JJA deductions (Employment)
    employment_deduction: Money = Money.zero()
    
    # Section 80JJAA deductions (Employment Generation)
    employment_generation_deduction: Money = Money.zero()
    
    # Section 80LA deductions (Offshore Banking)
    offshore_banking_deduction: Money = Money.zero()
    
    # Section 80P deductions (Co-operative Societies)
    co_operative_society_deduction: Money = Money.zero()
    
    # Section 80QQB deductions (Royalty)
    royalty_deduction: Money = Money.zero()
    
    # Section 80RRB deductions (Patent)
    patent_deduction: Money = Money.zero()
    
    # Section 80TTA deductions (Interest on Savings)
    interest_on_savings_deduction: Money = Money.zero()
    
    # Section 80U deductions (Disability)
    disability_deduction_amount: Money = Money.zero()
    
    def get_total_80c_deductions(self) -> Money:
        """Get total deductions under Section 80C."""
        return (
            self.life_insurance_premium
            .add(self.elss_investments)
            .add(self.public_provident_fund)
            .add(self.employee_provident_fund)
            .add(self.sukanya_samriddhi)
            .add(self.national_savings_certificate)
            .add(self.tax_saving_fixed_deposits)
            .add(self.principal_repayment_home_loan)
            .add(self.tuition_fees)
            .add(self.other_80c_deductions)
        )
    
    def get_total_80d_deductions(self) -> Money:
        """Get total deductions under Section 80D."""
        return (
            self.health_insurance_self
            .add(self.health_insurance_parents)
            .add(self.preventive_health_checkup)
        )
    
    def get_total_deductions(self) -> Money:
        """Get total of all deductions."""
        return (
            self.get_total_80c_deductions()
            .add(self.get_total_80d_deductions())
            .add(self.education_loan_interest)
            .add(self.donations_80g)
            .add(self.savings_account_interest)
            .add(self.senior_citizen_interest)
            .add(self.disability_deduction)
            .add(self.medical_treatment_deduction)
            .add(self.scientific_research_donation)
            .add(self.political_donation)
            .add(self.infrastructure_deduction)
            .add(self.industrial_undertaking_deduction)
            .add(self.special_category_state_deduction)
            .add(self.hotel_deduction)
            .add(self.north_eastern_state_deduction)
            .add(self.employment_deduction)
            .add(self.employment_generation_deduction)
            .add(self.offshore_banking_deduction)
            .add(self.co_operative_society_deduction)
            .add(self.royalty_deduction)
            .add(self.patent_deduction)
            .add(self.interest_on_savings_deduction)
            .add(self.disability_deduction_amount)
        )
    
    def calculate_80c_limit(self) -> Money:
        """Calculate Section 80C limit (₹1.5 lakh)."""
        max_limit = Money(Decimal('150000'))
        total_80c = self.get_total_80c_deductions()
        
        if total_80c.is_less_than(max_limit):
            return total_80c
        else:
            return max_limit
    
    def calculate_80d_limit(self, senior_citizen: bool = False) -> Money:
        """
        Calculate Section 80D limit.
        
        Args:
            senior_citizen: Whether taxpayer is senior citizen
            
        Returns:
            Money: Maximum allowed deduction
        """
        if senior_citizen:
            max_limit = Money(Decimal('50000'))  # ₹50,000 for senior citizens
        else:
            max_limit = Money(Decimal('25000'))  # ₹25,000 for others
        
        total_80d = self.get_total_80d_deductions()
        
        if total_80d.is_less_than(max_limit):
            return total_80d
        else:
            return max_limit
    
    def calculate_80tta_limit(self) -> Money:
        """Calculate Section 80TTA limit (₹10,000)."""
        max_limit = Money(Decimal('10000'))
        
        if self.savings_account_interest.is_less_than(max_limit):
            return self.savings_account_interest
        else:
            return max_limit
    
    def calculate_80ttb_limit(self) -> Money:
        """Calculate Section 80TTB limit (₹50,000)."""
        max_limit = Money(Decimal('50000'))
        
        if self.senior_citizen_interest.is_less_than(max_limit):
            return self.senior_citizen_interest
        else:
            return max_limit
    
    def calculate_80u_limit(self, disability_percentage: int) -> Money:
        """
        Calculate Section 80U limit based on disability percentage.
        
        Args:
            disability_percentage: Percentage of disability
            
        Returns:
            Money: Maximum allowed deduction
        """
        if disability_percentage >= 80:
            return Money(Decimal('125000'))  # ₹1.25 lakh for 80% or more
        elif disability_percentage >= 40:
            return Money(Decimal('75000'))   # ₹75,000 for 40% to 79%
        else:
            return Money.zero()
    
    def calculate_80ddb_limit(self, 
                            age: int,
                            disability_percentage: int) -> Money:
        """
        Calculate Section 80DDB limit.
        
        Args:
            age: Age of dependent
            disability_percentage: Percentage of disability
            
        Returns:
            Money: Maximum allowed deduction
        """
        if disability_percentage < 40:
            return Money.zero()
        
        if age < 60:
            return Money(Decimal('40000'))  # ₹40,000 for below 60
        elif age < 80:
            return Money(Decimal('100000'))  # ₹1 lakh for 60-80
        else:
            return Money(Decimal('125000'))  # ₹1.25 lakh for above 80 