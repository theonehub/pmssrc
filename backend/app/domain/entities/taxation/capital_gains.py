"""
Capital Gains Entity
Domain entity for handling capital gains calculations
"""

from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum
from decimal import Decimal
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CapitalGainsType(Enum):
    """Types of capital gains."""
    STCG_111A = "STCG 111A (Equity with STT)"
    STCG_OTHER = "STCG Other Assets"
    LTCG_112A = "LTCG 112A (Equity with STT)"
    LTCG_OTHER = "LTCG Other Assets"
    LTCG_DEBT_MF = "LTCG Debt Mutual Funds"


@dataclass
class CapitalGainsIncome:
    """Capital gains income calculation entity."""
    
    # Short-Term Capital Gains
    stcg_111a_equity_stt: Money = Money.zero()  # Equity with STT
    stcg_other_assets: Money = Money.zero()     # Other assets (taxed at slab rates)
    stcg_debt_mf: Money = Money.zero()          # Debt mutual funds
    
    # Long-Term Capital Gains
    ltcg_112a_equity_stt: Money = Money.zero()  # Equity with STT
    ltcg_other_assets: Money = Money.zero()     # Other assets
    ltcg_debt_mf: Money = Money.zero()          # Debt mutual funds
    
    def calculate_stcg_111a_tax(self) -> Money:
        """
        Calculate tax on STCG 111A (Equity with STT) at 20%.
        
        Returns:
            Money: Tax amount
        """
        # STCG 111A is taxed at 20% (Budget 2024)
        return self.stcg_111a_equity_stt.percentage(20)
    
    def calculate_ltcg_112a_tax(self) -> Money:
        """
        Calculate tax on LTCG 112A (Equity with STT) at 12.5% with ₹1.25L exemption.
        
        Returns:
            Money: Tax amount
        """
        # LTCG 112A exemption increased to ₹1.25 lakh (Budget 2024)
        exemption_limit = Money.from_int(125000)
        
        if self.ltcg_112a_equity_stt.is_greater_than(exemption_limit):
            taxable_ltcg = self.ltcg_112a_equity_stt.subtract(exemption_limit)
            # LTCG 112A is taxed at 12.5% (Budget 2024)
            return taxable_ltcg.percentage(Decimal('12.5'))
        
        return Money.zero()
    
    def calculate_ltcg_other_tax(self) -> Money:
        """
        Calculate tax on LTCG from other assets at 12.5%.
        
        Returns:
            Money: Tax amount
        """
        # LTCG from other assets taxed at 12.5% (Budget 2024)
        total_ltcg_other = self.ltcg_other_assets.add(self.ltcg_debt_mf)
        return total_ltcg_other.percentage(Decimal('12.5'))
    
    def calculate_total_capital_gains_tax(self) -> Money:
        """
        Calculate total capital gains tax.
        
        Returns:
            Money: Total capital gains tax
        """
        stcg_111a_tax = self.calculate_stcg_111a_tax()
        ltcg_112a_tax = self.calculate_ltcg_112a_tax()
        ltcg_other_tax = self.calculate_ltcg_other_tax()
        
        return stcg_111a_tax.add(ltcg_112a_tax).add(ltcg_other_tax)
    
    def calculate_stcg_for_slab_rates(self) -> Money:
        """
        Calculate STCG that will be taxed at slab rates (added to regular income).
        
        Returns:
            Money: STCG amount for slab taxation
        """
        logger.info(f"CGI: stcg_other_assets: {self.stcg_other_assets}")
        logger.info(f"CGI: stcg_debt_mf: {self.stcg_debt_mf}")
        return self.stcg_other_assets.add(self.stcg_debt_mf)
    
    def calculate_total_capital_gains_income(self) -> Money:
        """
        Calculate total capital gains income.
        
        Returns:
            Money: Total capital gains
        """
        total_stcg = (self.stcg_111a_equity_stt
                     .add(self.stcg_other_assets)
                     .add(self.stcg_debt_mf))
        
        total_ltcg = (self.ltcg_112a_equity_stt
                     .add(self.ltcg_other_assets)
                     .add(self.ltcg_debt_mf))
        
        return total_stcg.add(total_ltcg)
    
    def get_capital_gains_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """
        Get detailed breakdown of capital gains calculations.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Complete capital gains breakdown
        """
        stcg_111a_tax = self.calculate_stcg_111a_tax()
        ltcg_112a_tax = self.calculate_ltcg_112a_tax()
        ltcg_other_tax = self.calculate_ltcg_other_tax()
        total_cg_tax = self.calculate_total_capital_gains_tax()
        stcg_slab_rate = self.calculate_stcg_for_slab_rates()
        
        return {
            "regime": regime.regime_type.value,
            "short_term_capital_gains": {
                "stcg_111a_equity_stt": {
                    "amount": self.stcg_111a_equity_stt.to_float(),
                    "tax_rate": "20%",
                    "tax_amount": stcg_111a_tax.to_float()
                },
                "stcg_other_assets": {
                    "amount": self.stcg_other_assets.to_float(),
                    "tax_rate": "Slab rates",
                    "note": "Added to regular income"
                },
                "stcg_debt_mf": {
                    "amount": self.stcg_debt_mf.to_float(),
                    "tax_rate": "Slab rates",
                    "note": "Added to regular income"
                },
                "total_stcg_for_slab_rates": stcg_slab_rate.to_float()
            },
            "long_term_capital_gains": {
                "ltcg_112a_equity_stt": {
                    "amount": self.ltcg_112a_equity_stt.to_float(),
                    "exemption_limit": 125000,
                    "tax_rate": "12.5%",
                    "tax_amount": ltcg_112a_tax.to_float()
                },
                "ltcg_other_assets": {
                    "amount": self.ltcg_other_assets.to_float(),
                    "tax_rate": "12.5%",
                    "tax_amount": self.ltcg_other_assets.percentage(Decimal('12.5')).to_float()
                },
                "ltcg_debt_mf": {
                    "amount": self.ltcg_debt_mf.to_float(),
                    "tax_rate": "12.5%",
                    "tax_amount": self.ltcg_debt_mf.percentage(Decimal('12.5')).to_float()
                },
                "total_ltcg_tax": ltcg_other_tax.to_float()
            },
            "summary": {
                "total_capital_gains_income": self.calculate_total_capital_gains_income().to_float(),
                "total_capital_gains_tax": total_cg_tax.to_float(),
                "amount_added_to_regular_income": stcg_slab_rate.to_float(),
                "amount_taxed_separately": (self.stcg_111a_equity_stt
                                          .add(self.ltcg_112a_equity_stt)
                                          .add(self.ltcg_other_assets)
                                          .add(self.ltcg_debt_mf)).to_float()
            }
        }

    