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
    other_income: float = 0


    def get_section_80tt(self, age: int, regime: str = 'new'):
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
            self.other_income
        ])
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "regime": self.regime,
            "age": self.age,
            "interest_savings": self.interest_savings,
            "interest_fd": self.interest_fd,
            "interest_rd": self.interest_rd,
            "dividend_income": self.dividend_income,
            "gifts": self.gifts,
            "other_interest": self.other_interest,
            "other_income": self.other_income
        }


@dataclass
class IncomeFromHouseProperty:
    """
    Represents income from house property as per Indian Income Tax Act.
    Includes rental income, property tax, interest on home loan, etc.
    """
    property_address: str = ''
    occupancy_status: str = ''  # LetOut, SelfOccupied, PerConstruction
    rent_income: float = 0
    property_tax: float = 0
    interest_on_home_loan: float = 0

    def total_taxable_income_per_slab(self, regime: str = 'new'):
        """Calculate taxable income from house property."""
        standard_deduction = self.rent_income * 0.3
        if regime == 'New':
            if self.occupancy_status == 'LetOut':
                interest = self.interest_on_home_loan
            else:
                interest = 0
        elif self.occupancy_status == 'PerConstruction':
            interest = self.interest_on_home_loan * 0.2
        else:
            interest = self.interest_on_home_loan

        return self.rent_income - self.property_tax - standard_deduction - interest
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "property_address": self.property_address,
            "occupancy_status": self.occupancy_status,
            "rent_income": self.rent_income,
            "property_tax": self.property_tax,
            "interest_on_home_loan": self.interest_on_home_loan
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
    
    def total(self) -> float:
        """Calculate total capital gains."""
        return (
            self.total_stcg_special_rate() +
            self.total_stcg_slab_rate() +
            self.total_ltcg_special_rate()
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "stcg_111a": self.stcg_111a,
            "stcg_any_other_asset": self.stcg_any_other_asset,
            "stcg_debt_mutual_fund": self.stcg_debt_mutual_fund,
            "ltcg_112a": self.ltcg_112a,
            "ltcg_any_other_asset": self.ltcg_any_other_asset,
            "ltcg_debt_mutual_fund": self.ltcg_debt_mutual_fund
        }


@dataclass
class BusinessProfessionalIncome:
    """
    Represents business and professional income as per Indian Income Tax Act.
    """
    business_income: float = 0
    professional_income: float = 0
    
    def total_taxable_income_per_slab(self):
        """Calculate total taxable business and professional income."""
        return self.business_income + self.professional_income
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for JSON serialization."""
        return {
            "business_income": self.business_income,
            "professional_income": self.professional_income
        } 