"""
Other Income Entity
Represents various other sources of income
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.domain.value_objects.money import Money


@dataclass
class OtherIncome:
    """Other income entity containing various income sources."""
    
    # Interest income
    bank_interest: Money = Money.zero()
    fixed_deposit_interest: Money = Money.zero()
    recurring_deposit_interest: Money = Money.zero()
    post_office_interest: Money = Money.zero()
    other_interest: Money = Money.zero()
    
    # Dividend income
    equity_dividend: Money = Money.zero()
    mutual_fund_dividend: Money = Money.zero()
    other_dividend: Money = Money.zero()
    
    # Rental income
    house_property_rent: Money = Money.zero()
    commercial_property_rent: Money = Money.zero()
    other_rental: Money = Money.zero()
    
    # Business income
    business_income: Money = Money.zero()
    professional_income: Money = Money.zero()
    
    # Capital gains
    short_term_capital_gains: Money = Money.zero()
    long_term_capital_gains: Money = Money.zero()
    
    # Other sources
    lottery_winnings: Money = Money.zero()
    horse_race_winnings: Money = Money.zero()
    crossword_puzzle_winnings: Money = Money.zero()
    card_game_winnings: Money = Money.zero()
    other_speculative_income: Money = Money.zero()
    
    # Exempt income
    agricultural_income: Money = Money.zero()
    share_of_profit_partnership: Money = Money.zero()
    interest_on_tax_free_bonds: Money = Money.zero()
    other_exempt_income: Money = Money.zero()
    
    def get_total_interest_income(self) -> Money:
        """Get total interest income."""
        return (
            self.bank_interest
            .add(self.fixed_deposit_interest)
            .add(self.recurring_deposit_interest)
            .add(self.post_office_interest)
            .add(self.other_interest)
        )
    
    def get_total_dividend_income(self) -> Money:
        """Get total dividend income."""
        return (
            self.equity_dividend
            .add(self.mutual_fund_dividend)
            .add(self.other_dividend)
        )
    
    def get_total_rental_income(self) -> Money:
        """Get total rental income."""
        return (
            self.house_property_rent
            .add(self.commercial_property_rent)
            .add(self.other_rental)
        )
    
    def get_total_business_income(self) -> Money:
        """Get total business income."""
        return (
            self.business_income
            .add(self.professional_income)
        )
    
    def get_total_capital_gains(self) -> Money:
        """Get total capital gains."""
        return (
            self.short_term_capital_gains
            .add(self.long_term_capital_gains)
        )
    
    def get_total_speculative_income(self) -> Money:
        """Get total speculative income."""
        return (
            self.lottery_winnings
            .add(self.horse_race_winnings)
            .add(self.crossword_puzzle_winnings)
            .add(self.card_game_winnings)
            .add(self.other_speculative_income)
        )
    
    def get_total_exempt_income(self) -> Money:
        """Get total exempt income."""
        return (
            self.agricultural_income
            .add(self.share_of_profit_partnership)
            .add(self.interest_on_tax_free_bonds)
            .add(self.other_exempt_income)
        )
    
    def get_total_taxable_income(self) -> Money:
        """Get total taxable income."""
        return (
            self.get_total_interest_income()
            .add(self.get_total_dividend_income())
            .add(self.get_total_rental_income())
            .add(self.get_total_business_income())
            .add(self.get_total_capital_gains())
            .add(self.get_total_speculative_income())
        )
    
    def get_total_income(self) -> Money:
        """Get total income including exempt income."""
        return (
            self.get_total_taxable_income()
            .add(self.get_total_exempt_income())
        )
    
    def calculate_tax_on_speculative_income(self) -> Money:
        """
        Calculate tax on speculative income.
        Flat 30% tax rate on all speculative income.
        """
        return self.get_total_speculative_income().percentage(Decimal('30'))
    
    def calculate_tax_on_short_term_capital_gains(self) -> Money:
        """
        Calculate tax on short-term capital gains.
        Flat 15% tax rate on short-term capital gains.
        """
        return self.short_term_capital_gains.percentage(Decimal('15'))
    
    def calculate_tax_on_long_term_capital_gains(self) -> Money:
        """
        Calculate tax on long-term capital gains.
        Flat 10% tax rate on long-term capital gains above ₹1 lakh.
        """
        if self.long_term_capital_gains.is_less_than(Money(Decimal('100000'))):
            return Money.zero()
        else:
            return self.long_term_capital_gains.percentage(Decimal('10'))
    
    def calculate_tax_on_dividend_income(self) -> Money:
        """
        Calculate tax on dividend income.
        Flat 10% tax rate on dividend income.
        """
        return self.get_total_dividend_income().percentage(Decimal('10'))
    
    def calculate_tax_on_interest_income(self) -> Money:
        """
        Calculate tax on interest income.
        Interest income is taxed as per normal slab rates.
        """
        return self.get_total_interest_income()
    
    def calculate_tax_on_rental_income(self) -> Money:
        """
        Calculate tax on rental income.
        Rental income is taxed as per normal slab rates.
        """
        return self.get_total_rental_income()
    
    def calculate_tax_on_business_income(self) -> Money:
        """
        Calculate tax on business income.
        Business income is taxed as per normal slab rates.
        """
        return self.get_total_business_income() 