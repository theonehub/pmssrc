"""
Income source models for taxation calculations.

Contains classes for different types of income sources:
- Income from other sources (interest, dividends, etc.)
- Income from house property
- Capital gains (short term and long term)
- Business and professional income
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


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

    def total_taxable_income_per_slab(self, regime: str = 'new'):
        """Calculate taxable income from house property."""
        standard_deduction = self.rent_income * 0.3
        if regime == 'New':
            if self.occupancy_status == 'Let-Out':
                interest = self.interest_on_home_loan
            else:
                interest = 0
        elif self.occupancy_status == 'Per-Construction':
            interest = self.interest_on_home_loan * 0.2
        else:
            interest = self.interest_on_home_loan

        return self.rent_income - self.property_tax - standard_deduction - interest

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

    def total_stcg_special_rate(self):
        """Total short-term capital gains charged at special rates."""
        return self.stcg_111a
    
    def total_stcg_slab_rate(self):
        """Total short-term capital gains taxed at slab rates."""
        return self.stcg_any_other_asset + self.stcg_debt_mutual_fund
    
    def total_ltcg_special_rate(self):
        """Total long-term capital gains charged at special rates."""
        return self.ltcg_112a + self.ltcg_any_other_asset + self.ltcg_debt_mutual_fund
    
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



    def total_taxable_income_per_slab(self, regime: str = 'new') -> float:
        """Calculate total leave salary income."""
        max_deduction = 2500000  #25L
        #Get average salary for last 10 months from the salary slips for now assume it is 1L per month
        average_salary = 100000
        salary_last_10_months = average_salary * 10
        
        if self.leave_balance > (self.service_years * 30):
            deduction = average_salary * self.service_years
        else:
            deduction = average_salary * self.leave_balance

        deduction = min(deduction, max_deduction)
        taxable_income =  min(0, min(self.leave_encashment_income_received - deduction))

        return taxable_income

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "leave_encashment_income_received": cls.leave_encashment_income_received,
            "service_years": cls.service_years,
            "leave_balance": cls.leave_balance
        }
    
    