"""
Other Income Entity
Domain entity for handling income from other sources
"""

from dataclasses import dataclass
from typing import Dict, Any
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType


@dataclass
class InterestIncome:
    """Interest income from various sources."""
    
    savings_account_interest: Money = Money.zero()
    fixed_deposit_interest: Money = Money.zero()
    recurring_deposit_interest: Money = Money.zero()
    other_bank_interest: Money = Money.zero()
    age: int = 25
    
    def calculate_total_interest(self) -> Money:
        """Calculate total interest income."""
        return (self.savings_account_interest
                .add(self.fixed_deposit_interest)
                .add(self.recurring_deposit_interest)
                .add(self.other_bank_interest))
    
    def calculate_exemption_80tta_80ttb(self, regime: TaxRegime) -> Money:
        """Calculate interest exemption under 80TTA/80TTB."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if self.age >= 60:
            # Section 80TTB - All bank interest up to Rs. 50,000
            total_interest = self.calculate_total_interest()
            max_limit = Money.from_int(50000)
            return total_interest.min(max_limit)
        else:
            # Section 80TTA - Only savings interest up to Rs. 10,000
            max_limit = Money.from_int(10000)
            return self.savings_account_interest.min(max_limit)
    
    def calculate_taxable_interest(self, regime: TaxRegime) -> Money:
        """Calculate taxable interest income."""
        total_interest = self.calculate_total_interest()
        exemption = self.calculate_exemption_80tta_80ttb(regime)
        return total_interest.subtract(exemption).max(Money.zero())
    
    def get_interest_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """Get detailed breakdown of interest income."""
        exemption = self.calculate_exemption_80tta_80ttb(regime)
        
        return {
            "savings_interest": self.savings_account_interest.to_float(),
            "fd_interest": self.fixed_deposit_interest.to_float(),
            "rd_interest": self.recurring_deposit_interest.to_float(),
            "other_bank_interest": self.other_bank_interest.to_float(),
            "total_interest": self.calculate_total_interest().to_float(),
            "applicable_section": "80TTB" if self.age >= 60 else "80TTA",
            "exemption_limit": 50000 if self.age >= 60 else 10000,
            "exemption_claimed": exemption.to_float(),
            "taxable_interest": self.calculate_taxable_interest(regime).to_float()
        }


@dataclass
class OtherIncome:
    """Complete other income entity."""
    
    # Interest income
    interest_income: InterestIncome = None
    
    # Other income sources (fully taxable)
    dividend_income: Money = Money.zero()
    gifts_received: Money = Money.zero()
    business_professional_income: Money = Money.zero()
    other_miscellaneous_income: Money = Money.zero()
    
    def __post_init__(self):
        """Initialize interest income if not provided."""
        if self.interest_income is None:
            self.interest_income = InterestIncome()
    
    def calculate_total_other_income(self, regime: TaxRegime) -> Money:
        """
        Calculate total income from other sources.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Total other income
        """
        total = Money.zero()
        
        # Add taxable interest income (after exemptions)
        total = total.add(self.interest_income.calculate_taxable_interest(regime))
        
        # Add other income sources (fully taxable)
        total = total.add(self.dividend_income)
        total = total.add(self.gifts_received)
        total = total.add(self.business_professional_income)
        total = total.add(self.other_miscellaneous_income)
        
        return total
    
    def get_other_income_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """
        Get detailed breakdown of other income.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Complete other income breakdown
        """
        return {
            "regime": regime.regime_type.value,
            "interest_income": self.interest_income.get_interest_breakdown(regime),
            "other_income_sources": {
                "dividend_income": self.dividend_income.to_float(),
                "gifts_received": self.gifts_received.to_float(),
                "business_professional_income": self.business_professional_income.to_float(),
                "other_miscellaneous_income": self.other_miscellaneous_income.to_float(),
                "total_other_sources": (self.dividend_income
                                      .add(self.gifts_received)
                                      .add(self.business_professional_income)
                                      .add(self.other_miscellaneous_income)).to_float()
            },
            "total_other_income": self.calculate_total_other_income(regime).to_float()
        }
    
    # Backward compatibility properties for legacy code
    @property
    def bank_interest(self) -> Money:
        """Backward compatibility: Get bank interest (savings account interest)."""
        return self.interest_income.savings_account_interest if self.interest_income else Money.zero()
    
    @property
    def fixed_deposit_interest(self) -> Money:
        """Backward compatibility: Get fixed deposit interest."""
        return self.interest_income.fixed_deposit_interest if self.interest_income else Money.zero()
    
    @property
    def recurring_deposit_interest(self) -> Money:
        """Backward compatibility: Get recurring deposit interest."""
        return self.interest_income.recurring_deposit_interest if self.interest_income else Money.zero()
    
    @property
    def post_office_interest(self) -> Money:
        """Backward compatibility: Get post office interest (mapped to other bank interest)."""
        return self.interest_income.other_bank_interest if self.interest_income else Money.zero()
    
    @property
    def other_interest(self) -> Money:
        """Backward compatibility: Get other interest (mapped to other bank interest)."""
        return self.interest_income.other_bank_interest if self.interest_income else Money.zero()
    
    @property
    def equity_dividend(self) -> Money:
        """Backward compatibility: Get equity dividend (mapped to dividend income)."""
        return self.dividend_income
    
    @property
    def mutual_fund_dividend(self) -> Money:
        """Backward compatibility: Get mutual fund dividend (default to zero)."""
        return Money.zero()
    
    @property
    def other_dividend(self) -> Money:
        """Backward compatibility: Get other dividend (default to zero)."""
        return Money.zero()
    
    @property
    def house_property_rent(self) -> Money:
        """Backward compatibility: Get house property rent (default to zero)."""
        return Money.zero()
    
    @property
    def commercial_property_rent(self) -> Money:
        """Backward compatibility: Get commercial property rent (default to zero)."""
        return Money.zero()
    
    @property
    def other_rental(self) -> Money:
        """Backward compatibility: Get other rental (default to zero)."""
        return Money.zero()
    
    @property
    def business_income(self) -> Money:
        """Backward compatibility: Get business income (mapped to business_professional_income)."""
        return self.business_professional_income
    
    @property
    def professional_income(self) -> Money:
        """Backward compatibility: Get professional income (mapped to business_professional_income)."""
        return self.business_professional_income
    
    @property
    def short_term_capital_gains(self) -> Money:
        """Backward compatibility: Get short term capital gains (default to zero)."""
        return Money.zero()
    
    @property
    def long_term_capital_gains(self) -> Money:
        """Backward compatibility: Get long term capital gains (default to zero)."""
        return Money.zero()
    
    @property
    def lottery_winnings(self) -> Money:
        """Backward compatibility: Get lottery winnings (default to zero)."""
        return Money.zero()
    
    @property
    def horse_race_winnings(self) -> Money:
        """Backward compatibility: Get horse race winnings (default to zero)."""
        return Money.zero()
    
    @property
    def crossword_puzzle_winnings(self) -> Money:
        """Backward compatibility: Get crossword puzzle winnings (default to zero)."""
        return Money.zero()
    
    @property
    def card_game_winnings(self) -> Money:
        """Backward compatibility: Get card game winnings (default to zero)."""
        return Money.zero()
    
    @property
    def other_speculative_income(self) -> Money:
        """Backward compatibility: Get other speculative income (mapped to other_miscellaneous_income)."""
        return self.other_miscellaneous_income
    
    @property
    def agricultural_income(self) -> Money:
        """Backward compatibility: Get agricultural income (default to zero)."""
        return Money.zero()
    
    @property
    def share_of_profit_partnership(self) -> Money:
        """Backward compatibility: Get share of profit from partnership (default to zero)."""
        return Money.zero()
    
    @property
    def interest_on_tax_free_bonds(self) -> Money:
        """Backward compatibility: Get interest on tax free bonds (default to zero)."""
        return Money.zero()
    
    @property
    def other_exempt_income(self) -> Money:
        """Backward compatibility: Get other exempt income (default to zero)."""
        return Money.zero() 