"""
Capital Gains Income Entity
Represents income from capital gains
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import date

from app.domain.value_objects.money import Money


@dataclass
class CapitalGainsIncome:
    """Capital gains income entity containing capital gains details."""
    
    # Asset details
    asset_type: str  # equity, debt, property, etc.
    purchase_date: date
    sale_date: date
    purchase_price: Money
    sale_price: Money
    transfer_expenses: Money = Money.zero()
    improvement_cost: Money = Money.zero()
    
    # Additional details
    is_listed_security: bool = False
    is_residential_property: bool = False
    is_agricultural_land: bool = False
    is_business_asset: bool = False
    
    def get_holding_period(self) -> int:
        """
        Calculate holding period in years.
        
        Returns:
            int: Number of years the asset was held
        """
        years = self.sale_date.year - self.purchase_date.year
        if (self.sale_date.month, self.sale_date.day) < (self.purchase_date.month, self.purchase_date.day):
            years -= 1
        return years
    
    def is_long_term(self) -> bool:
        """
        Check if capital gain is long-term.
        
        Long-term holding periods:
        - Equity/debt mutual funds: 1 year
        - Property: 2 years
        - Other assets: 3 years
        """
        holding_period = self.get_holding_period()
        
        if self.asset_type in ["equity", "debt"]:
            return holding_period >= 1
        elif self.asset_type == "property":
            return holding_period >= 2
        else:
            return holding_period >= 3
    
    def get_cost_of_acquisition(self) -> Money:
        """
        Calculate cost of acquisition.
        
        Cost of acquisition = Purchase price + Transfer expenses + Improvement cost
        """
        return (
            self.purchase_price
            .add(self.transfer_expenses)
            .add(self.improvement_cost)
        )
    
    def get_capital_gain(self) -> Money:
        """
        Calculate capital gain.
        
        Capital gain = Sale price - Cost of acquisition
        """
        return self.sale_price.subtract(self.get_cost_of_acquisition())
    
    def get_indexed_cost_of_acquisition(self, 
                                      purchase_year_index: Decimal,
                                      sale_year_index: Decimal) -> Money:
        """
        Calculate indexed cost of acquisition.
        
        Indexed cost = Cost of acquisition × (Sale year index / Purchase year index)
        
        Args:
            purchase_year_index: Cost inflation index for purchase year
            sale_year_index: Cost inflation index for sale year
            
        Returns:
            Money: Indexed cost of acquisition
        """
        if not self.is_long_term():
            return self.get_cost_of_acquisition()
        
        indexed_cost = (
            self.get_cost_of_acquisition().amount
            * (sale_year_index / purchase_year_index)
        )
        
        return Money(Decimal(str(indexed_cost)))
    
    def get_indexed_capital_gain(self,
                               purchase_year_index: Decimal,
                               sale_year_index: Decimal) -> Money:
        """
        Calculate indexed capital gain.
        
        Indexed capital gain = Sale price - Indexed cost of acquisition
        
        Args:
            purchase_year_index: Cost inflation index for purchase year
            sale_year_index: Cost inflation index for sale year
            
        Returns:
            Money: Indexed capital gain
        """
        return self.sale_price.subtract(
            self.get_indexed_cost_of_acquisition(purchase_year_index, sale_year_index)
        )
    
    def get_taxable_capital_gain(self) -> Money:
        """
        Calculate taxable capital gain.
        
        For long-term capital gains:
        - Equity/debt mutual funds: 10% tax on gains above ₹1 lakh
        - Property: 20% tax on indexed gains
        - Other assets: 20% tax on indexed gains
        
        For short-term capital gains:
        - Equity: 15% tax
        - Other assets: Normal slab rates
        """
        if not self.is_long_term():
            # Short-term capital gains
            if self.asset_type == "equity":
                return self.get_capital_gain().percentage(Decimal('15'))
            else:
                return self.get_capital_gain()
        else:
            # Long-term capital gains
            if self.asset_type in ["equity", "debt"]:
                gain = self.get_capital_gain()
                if gain.is_less_than(Money(Decimal('100000'))):
                    return Money.zero()
                else:
                    return gain.percentage(Decimal('10'))
            else:
                # For property and other assets, use indexed gains
                return self.get_indexed_capital_gain(
                    Decimal('100'),  # Placeholder for purchase year index
                    Decimal('100')   # Placeholder for sale year index
                ).percentage(Decimal('20'))
    
    def get_exempt_capital_gain(self) -> Money:
        """
        Calculate exempt capital gain.
        
        Exemptions available:
        - Investment in residential property
        - Investment in specified bonds
        - Investment in startup
        """
        # TODO: Implement exemption calculations based on investment details
        return Money.zero()
    
    def get_net_taxable_capital_gain(self) -> Money:
        """
        Calculate net taxable capital gain.
        
        Net taxable gain = Taxable gain - Exempt gain
        """
        return self.get_taxable_capital_gain().subtract(self.get_exempt_capital_gain())
    
    def get_asset_type_description(self) -> str:
        """Get human-readable asset type description."""
        if self.asset_type == "equity":
            return "Equity Shares"
        elif self.asset_type == "debt":
            return "Debt Instruments"
        elif self.asset_type == "property":
            return "Property"
        else:
            return "Other Assets"
    
    def get_gain_type_description(self) -> str:
        """Get human-readable gain type description."""
        if self.is_long_term():
            return "Long-term Capital Gain"
        else:
            return "Short-term Capital Gain" 