"""
Income source models for taxation calculations.

Contains classes for different types of income sources:
- Income from other sources (interest, dividends, etc.)
- Income from house property
- Capital gains (short term and long term)
- Business and professional income
"""

from dataclasses import dataclass
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class IncomeFromOtherSources:
    """
    Represents income from other sources as per Indian Income Tax Act.
    Includes interest income, dividends, gifts and other sources.
    """
    regime: str = 'new'
    age: int = 0
    interest_savings: float = 0
    interest_fd: float = 0
    interest_rd: float = 0
    dividend_income: float = 0
    gifts: float = 0
    other_interest: float = 0
    business_professional_income: float = 0
    other_income: float = 0


    @classmethod
    def get_section_80tt(cls, age: int, regime: str = 'new'):
        """Determine the applicable section for interest income based on age and regime."""
        if regime == 'old':
            if age >= 60:
                return "80TTB"
            else:
                return "80TTC"
        else:
            return "Not Applicable"

    def total_taxable_income_per_slab(self, regime: str = 'new', age: int = 0):
        """Calculate taxable income per slab with applicable deductions."""
        deduction = 10000
        if regime == 'new':
            return 0
        
        elif regime == 'old':
            if age >= 60:
                deduction = 50000

        return max(0, sum([
            self.interest_savings,
            self.interest_fd,
            self.interest_rd,
            self.dividend_income,
            self.gifts,
            self.other_interest,
            self.business_professional_income,
            self.other_income
        ]) - deduction)

    def total(self) -> float:
        """Calculate total income from other sources."""
        return sum([
            self.interest_savings,
            self.interest_fd,
            self.interest_rd,
            self.dividend_income,
            self.gifts,
            self.other_interest,
            self.business_professional_income,
            self.other_income
        ])
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "regime": cls.regime,
            "age": cls.age,
            "interest_savings": cls.interest_savings,
            "interest_fd": cls.interest_fd,
            "interest_rd": cls.interest_rd,
            "dividend_income": cls.dividend_income,
            "gifts": cls.gifts,
            "other_interest": cls.other_interest,
            "business_professional_income": cls.business_professional_income,
            "other_income": cls.other_income
        }


@dataclass
class IncomeFromHouseProperty:
    """
    Represents income from house property as per Indian Income Tax Act.
    Includes rental income, property tax, interest on home loan, etc.
    """
    property_address: str = ''
    occupancy_status: str = ''  # Let-Out, Self-Occupied, Per-Construction
    rent_income: float = 0
    property_tax: float = 0
    interest_on_home_loan: float = 0

    
    def calculate_annual_value(self) -> float:
        """
        Calculate annual value of house property.
        For Let-Out property: Rent income - Unrealized rent - Municipal tax paid
        For Self-Occupied property: Annual value is zero
        """
        if self.occupancy_status == 'Self-Occupied':
            logger.info(f"Self-Occupied property: Annual value set to 0")
            return 0
        
        # For Let-Out or Deemed Let-Out property
        annual_value = self.rent_income - self.property_tax
        logger.info(f"Calculating annual value: Rent {self.rent_income} - Property Tax {self.property_tax} = {annual_value}")
        return max(0, annual_value)

    def total_taxable_income_per_slab(self, regime: str = 'old') -> float:
        """
        Calculate taxable income from house property.
        
        For Let-Out property:
        Net Annual Value = Annual Value - Standard Deduction (30%) - Interest on Home Loan
        
        For Self-Occupied property:
        Interest deduction up to 2 lakh (for loans taken after 1999)
        """
        logger.info(f"Calculating income from house property for regime: {regime}")
        logger.info(f"Property status: {self.occupancy_status}, Rent: {self.rent_income}, Property Tax: {self.property_tax}, Interest: {self.interest_on_home_loan}")
        
        # Calculate annual value
        annual_value = self.calculate_annual_value()
        
        if self.occupancy_status == 'Self-Occupied':
            # For self-occupied property, only interest is deductible (up to 2 lakh)
            interest_deduction = min(self.interest_on_home_loan, 200000)
            annual_value = -interest_deduction
            logger.info(f"Self-Occupied property: Interest deduction {interest_deduction}, Net income: {annual_value}")
            return annual_value
        
        elif self.occupancy_status == 'Per-Construction':
            # Pre-construction interest is deductible in 5 equal installments
            # after construction is completed
            pre_construction_interest = self.interest_on_home_loan * 0.2
            logger.info(f"Per-Construction property: Interest deduction (1/5th) {pre_construction_interest}")
            return annual_value - pre_construction_interest
        
        else:  # Let-Out or Deemed Let-Out
            # Calculate standard deduction (30% of annual value)
            standard_deduction = annual_value * 0.3
            
            # Net annual value after standard deduction and interest
            net_income = annual_value - standard_deduction - self.interest_on_home_loan
            
            # Maximum loss allowed is -2 lakh
            if net_income < 200000:
                logger.info(f"Let-Out property: Annual value {annual_value}, Standard deduction {standard_deduction}, Interest {self.interest_on_home_loan}")
                logger.info(f"Loss from house property capped at -2 lakh (from {net_income})")
                return 200000
            
            logger.info(f"Let-Out property: Annual value {annual_value}, Standard deduction {standard_deduction}, Interest {self.interest_on_home_loan}, Net income: {net_income}")
            return net_income

    @classmethod    
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "property_address": cls.property_address,
            "occupancy_status": cls.occupancy_status,
            "rent_income": cls.rent_income,
            "property_tax": cls.property_tax,
            "interest_on_home_loan": cls.interest_on_home_loan
        }


@dataclass
class CapitalGains:
    """
    Represents capital gains income as per Indian Income Tax Act.
    Includes both short-term and long-term capital gains from various assets.
    """
    stcg_111a: float = 0    # Short Term Capital Gain from listed equity shares 
                            # and equity oriented mutual funds which are charged to STT
                            # (taxed at 20%)
    stcg_any_other_asset: float = 0     # Short Term Capital Gain from other assets 
                                        # (taxed at slab rates)
    stcg_debt_mutual_fund: float = 0    # Short Term Capital Gain from debt mutual funds 
                                        # (taxed at slab rates)
    
    ltcg_112a: float = 0    # Long Term Capital Gain from listed equity shares 
                            # and equity oriented mutual funds which are charged to STT 
                            # (12.5% above 1.25L)
    ltcg_any_other_asset: float = 0     # Long Term Capital Gain from other assets 
                                        # (taxed at 12.5%)
    ltcg_debt_mutual_fund: float = 0    # Long Term Capital Gain from debt mutual funds 
                                        # (taxed at 12.5%)

    def total_stcg_special_rate(self) -> float:
        """Total short-term capital gains charged at special rates."""
        logger.info(f"STCG at special rate (under section 111A): {self.stcg_111a}")
        return self.stcg_111a
    
    def total_stcg_slab_rate(self) -> float:
        """Total short-term capital gains taxed at slab rates."""
        total = self.stcg_any_other_asset + self.stcg_debt_mutual_fund
        logger.info(f"STCG at slab rates: {total}")
        return total
    
    def total_ltcg_special_rate(self) -> float:
        """Total long-term capital gains charged at special rates."""
        total = self.ltcg_112a + self.ltcg_any_other_asset + self.ltcg_debt_mutual_fund
        logger.info(f"LTCG at special rates: {total}")
        return total
        
    def total_ltcg_slab_rate(self) -> float:
        """Total long-term capital gains taxed at slab rates (should be zero as all LTCG has special rates)."""
        return 0
    
    def calculate_ltcg_tax(self) -> tuple:
        """
        Calculate taxable LTCG amounts according to tax rules.
        Returns a tuple of (ltcg_112a_taxable, ltcg_other_taxable)
        """
        # LTCG under 112A has 1L exemption
        ltcg_112a_taxable = max(0, self.ltcg_112a - 125000)
        
        # Other LTCG assets taxed at 20% with indexation benefit (already calculated in input values)
        ltcg_other_taxable = self.ltcg_any_other_asset + self.ltcg_debt_mutual_fund
        
        logger.info(f"LTCG under 112A: {self.ltcg_112a}, Exemption: 125000, Taxable: {ltcg_112a_taxable}")
        logger.info(f"LTCG other assets: {self.ltcg_any_other_asset + self.ltcg_debt_mutual_fund}")
        
        return (ltcg_112a_taxable, ltcg_other_taxable)
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "stcg_111a": cls.stcg_111a,
            "stcg_any_other_asset": cls.stcg_any_other_asset,
            "stcg_debt_mutual_fund": cls.stcg_debt_mutual_fund,
            "ltcg_112a": cls.ltcg_112a,
            "ltcg_any_other_asset": cls.ltcg_any_other_asset,
            "ltcg_debt_mutual_fund": cls.ltcg_debt_mutual_fund
        }
    
@dataclass
class LeaveEncashment:
    """
    Represents leave encashment income as per Indian Income Tax Act.
    Includes leave encashment income from various sources.
    """
    leave_encashment_income_received: float = 0
    service_years: int = 0
    leave_balance: float = 0
    average_monthly_salary: float = 100000  # TODO: Default value, should be properly calculated from salary history



    def total_taxable_income_per_slab(self, regime: str = 'old') -> float:
        """
        Calculate taxable leave encashment income.
        
        Exemption is least of:
        1. Actual leave encashment received
        2. 10 months' average salary (assumed as 100000 per month)
        3. Maximum exemption limit (₹25,00,000)
        4. Average salary × unexpired leave (30 days per year calculated for service years)
        """
        if regime == 'new':
            # In new regime, leave encashment is fully taxable
            logger.info(f"New regime - Leave encashment fully taxable: {self.leave_encashment_income_received}")
            return self.leave_encashment_income_received
            
        logger.info(f"Calculating leave encashment for regime: {regime}")
        logger.info(f"Leave encashment received: {self.leave_encashment_income_received}")
        logger.info(f"Service years: {self.service_years}")
        logger.info(f"Leave balance: {self.leave_balance}")
        logger.info(f"Average monthly salary: {self.average_monthly_salary}")
        
        # Calculate all possible exemption amounts
        actual_received = self.leave_encashment_income_received
        ten_months_salary = self.average_monthly_salary * 10
        statutory_limit = 2500000
        
        # Calculate unexpired leave based on service years
        # Assume entitlement of 30 days per year and calculate unused leave value
        salary_per_day = self.average_monthly_salary / 30
        if self.leave_balance > 0:
            # If leave balance is provided, use it directly
            unexpired_leave_value = self.leave_balance * salary_per_day
        else:
            # Otherwise calculate based on service years (assuming 30 days per year)
            unexpired_leave_value = self.service_years * 30 * salary_per_day
        
        # Exemption is the least of the four amounts
        exemption = min(actual_received, ten_months_salary, statutory_limit, unexpired_leave_value)
        
        # Taxable amount is received amount minus exemption
        taxable_amount = max(0, self.leave_encashment_income_received - exemption)
        
        logger.info(f"Leave encashment exemption calculation:")
        logger.info(f"Actual received: {actual_received}")
        logger.info(f"10 months salary: {ten_months_salary}")
        logger.info(f"Statutory limit: {statutory_limit}")
        logger.info(f"Unexpired leave value: {unexpired_leave_value}")
        logger.info(f"Exemption amount: {exemption}")
        logger.info(f"Taxable amount: {taxable_amount}")
        
        return taxable_amount

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "leave_encashment_income_received": cls.leave_encashment_income_received,
            "service_years": cls.service_years,
            "leave_balance": cls.leave_balance
        }
    
    