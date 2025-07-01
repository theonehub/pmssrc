"""
Other Income Entity
Domain entity for handling income from other sources
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.domain.entities.taxation.house_property_income import HousePropertyIncome
from app.domain.entities.taxation.capital_gains import CapitalGainsIncome
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class InterestIncome:
    """Interest income from various sources."""
    
    savings_account_interest: Money = Money.zero()
    fixed_deposit_interest: Money = Money.zero()
    recurring_deposit_interest: Money = Money.zero()
    post_office_interest: Money = Money.zero()
    
    def calculate_total_interest(self) -> Money:
        """Calculate total interest income."""
        logger.info(f"II: savings_account_interest: {self.savings_account_interest}")
        logger.info(f"II: fixed_deposit_interest: {self.fixed_deposit_interest}")
        logger.info(f"II: recurring_deposit_interest: {self.recurring_deposit_interest}")
        logger.info(f"II: post_office_interest: {self.post_office_interest}")
        return (self.savings_account_interest
                .add(self.fixed_deposit_interest)
                .add(self.recurring_deposit_interest)
                .add(self.post_office_interest))
    
    def calculate_exemption_80tta_80ttb(self, regime: TaxRegime, age: int) -> Money:
        """Calculate interest exemption under 80TTA/80TTB."""
        if regime.regime_type == TaxRegimeType.NEW:
            return Money.zero()
        
        if age >= 60:
            # Section 80TTB - All bank interest up to Rs. 50,000
            total_interest = self.calculate_total_interest()
            max_limit = Money.from_int(50000)
            logger.info(f"II: calculate_exemption_80tta_80ttb: max_limit: {max_limit}")
            return total_interest.min(max_limit)
        else:
            # Section 80TTA - Only savings interest up to Rs. 10,000
            max_limit = Money.from_int(10000)
            logger.info(f"II: calculate_exemption_80tta_80ttb: savings_account_interest: {self.savings_account_interest}")
            logger.info(f"II: calculate_exemption_80tta_80ttb: post_office_interest: {self.post_office_interest}")
            logger.info(f"II: calculate_exemption_80tta_80ttb: max_limit: {max_limit}")
            return self.savings_account_interest.add(self.post_office_interest).min(max_limit)
    
    def calculate_taxable_interest(self, regime: TaxRegime, age: int) -> Money:
        """Calculate taxable interest income."""
        logger.info(f"II: calculate_taxable_interest: regime: {regime}")
        logger.info(f"II: calculate_taxable_interest: age: {age}")
        total_interest = self.calculate_total_interest()
        logger.info(f"II: calculate_taxable_interest: total_interest: {total_interest}")
        exemption = self.calculate_exemption_80tta_80ttb(regime, age)
        logger.info(f"II: calculate_taxable_interest: exemption: {exemption}")
        return total_interest.subtract(exemption).max(Money.zero())
    
    def get_interest_breakdown(self, regime: TaxRegime, age: int) -> Dict[str, Any]:
        """Get detailed breakdown of interest income."""
        exemption = self.calculate_exemption_80tta_80ttb(regime, age)
        
        return {
            "savings_interest": self.savings_account_interest.to_float(),
            "fd_interest": self.fixed_deposit_interest.to_float(),
            "rd_interest": self.recurring_deposit_interest.to_float(),
            "post_office_interest": self.post_office_interest.to_float(),
            "total_interest": self.calculate_total_interest().to_float(),
            "applicable_section": "80TTB" if age >= 60 else "80TTA",
            "exemption_limit": 50000 if age >= 60 else 10000,
            "exemption_claimed": exemption.to_float(),
            "taxable_interest": self.calculate_taxable_interest(regime, age).to_float()
        }


@dataclass
class OtherIncome:
    """Complete other income entity."""
    
    business_professional_income: Money = Money.zero()
    house_property_income: HousePropertyIncome = None
    # Interest income
    interest_income: InterestIncome = None

    # Other income sources (fully taxable)
    dividend_income: Money = Money.zero()
    gifts_received: Money = Money.zero()
    other_miscellaneous_income: Money = Money.zero()
    capital_gains_income: Optional[CapitalGainsIncome] = None
    
    def __post_init__(self):
        """Initialize interest income if not provided."""
        if self.interest_income is None:
            self.interest_income = InterestIncome()

    def calculate_taxable_gifts_received(self, regime: TaxRegime) -> Money:
        """Calculate taxable gifts received."""
        """if gifts received is less than 50000, return zero or else return gifts received"""
        if regime.regime_type == TaxRegimeType.NEW:
            return self.gifts_received

        logger.info(f"Gift: gifts_received: {self.gifts_received} and max limit: {Money.from_int(50000)}")
        if self.gifts_received < Money.from_int(50000):
            return Money.zero()
        else:
            return self.gifts_received
        
    
    def calculate_total_other_income_slab_rates(self, regime: TaxRegime, age: int = 25) -> Money:
        """
        Calculate total income from other sources.
        
        Args:
            regime: Tax regime
            age: Taxpayer age for interest exemptions
            
        Returns:
            Money: Total other income
        """
        total = Money.zero()

        logger.info(f"BPI: business_professional_income: {self.business_professional_income}")
        # Add business professional income
        total = total.add(self.business_professional_income)

        # Add house property income (if any)
        if self.house_property_income:
            total = total.add(
                self.house_property_income.calculate_net_income_from_house_property(regime)
            )
        
        # Add taxable interest income (after exemptions)
        total = total.add(self.interest_income.calculate_taxable_interest(regime, age))
        logger.info(f"II: total interest income after exemptions: {total}")
        
        # Add capital gains income that goes to slab rates (if any)
        if self.capital_gains_income:
            stcg_for_slab_rates = self.capital_gains_income.calculate_stcg_for_slab_rates()
            logger.info(f"CGI: stcg_for_slab_rates: {stcg_for_slab_rates}")
            total = total.add(stcg_for_slab_rates)
        
        # Add other income sources (fully taxable)
        total = total.add(self.dividend_income)
        logger.info("Dividend income: ", self.dividend_income)
        total = total.add(self.calculate_taxable_gifts_received(regime))
        logger.info(f"II: total gifts received: {total}")
        total = total.add(self.other_miscellaneous_income)
        
        return total
    
    def calculate_interest_exemptions(self, regime: TaxRegime, age: int = 25) -> Money:
        """
        Calculate total exemptions from interest income.
        
        Args:
            regime: Tax regime
            age: Taxpayer age
            
        Returns:
            Money: Total interest exemptions
        """
        return self.interest_income.calculate_exemption_80tta_80ttb(regime, age)
    
    def calculate_capital_gains_tax_amount(self, regime: TaxRegime) -> Money:
        """
        Calculate total exemptions from capital gains.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Total capital gains exemptions (separate tax)
        """
        if self.capital_gains_income:
            return self.capital_gains_income.calculate_total_capital_gains_tax()
        return Money.zero()
    
    def get_other_income_breakdown(self, regime: TaxRegime, age: int = 25) -> Dict[str, Any]:
        """
        Get detailed breakdown of other income.
        
        Args:
            regime: Tax regime
            age: Taxpayer age
            
        Returns:
            Dict: Complete other income breakdown
        """
        breakdown = {
            "regime": regime.regime_type.value,
            "interest_income": self.interest_income.get_interest_breakdown(regime, age),
            "other_income_sources": {
                "dividend_income": self.dividend_income.to_float(),
                "gifts_received": self.gifts_received.to_float(),
                "business_professional_income": self.business_professional_income.to_float(),
                "other_miscellaneous_income": self.other_miscellaneous_income.to_float(),
                "total_other_sources": (self.dividend_income
                                      .add(self.calculate_taxable_gifts_received(regime))
                                      .add(self.business_professional_income)
                                      .add(self.other_miscellaneous_income)).to_float()
            },
            "total_other_income": self.calculate_total_other_income_slab_rates(regime, age).to_float()
        }
        
        # Add house property breakdown if present
        if self.house_property_income:
            breakdown["house_property_income"] = {
                "net_income": self.house_property_income.calculate_net_income_from_house_property(regime).to_float(),
                "breakdown": self.house_property_income.get_house_property_breakdown(regime)
            }
        
        # Add capital gains breakdown if present
        if self.capital_gains_income:
            breakdown["capital_gains_income"] = {
                "slab_rate_income": self.capital_gains_income.calculate_stcg_for_slab_rates().to_float(),
                "separate_tax": self.capital_gains_income.calculate_total_capital_gains_tax().to_float(),
                "breakdown": self.capital_gains_income.get_capital_gains_breakdown(regime)
            }
        
        return breakdown

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
    def other_bank_interest(self) -> Money:
        """Backward compatibility: Get other bank interest (mapped to post office interest)."""
        return self.interest_income.post_office_interest if self.interest_income else Money.zero()
    
    @property
    def other_interest(self) -> Money:
        """Backward compatibility: Get other interest (mapped to post office interest)."""
        return self.interest_income.post_office_interest if self.interest_income else Money.zero()
    
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
        """Backward compatibility: Get house property rent."""
        if self.house_property_income:
            return self.house_property_income.annual_rent_received
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