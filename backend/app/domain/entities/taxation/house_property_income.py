"""
House Property Income Entity
Represents income from house property
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.domain.value_objects.money import Money


@dataclass
class HousePropertyIncome:
    """House property income entity containing property details and income."""
    
    # Property details
    property_type: str  # self-occupied, let-out, deemed-let
    municipal_value: Money
    fair_rental_value: Money
    standard_rent: Money
    actual_rent: Money
    
    # Deductions
    municipal_tax: Money = Money.zero()
    interest_on_loan: Money = Money.zero()
    pre_construction_interest: Money = Money.zero()
    other_deductions: Money = Money.zero()
    
    # Additional details
    construction_completed: bool = True
    construction_year: Optional[int] = None
    loan_taken: bool = False
    loan_taken_year: Optional[int] = None
    
    def get_gross_annual_value(self) -> Money:
        """
        Calculate Gross Annual Value (GAV) of the property.
        
        For self-occupied property:
        - GAV is zero
        
        For let-out property:
        - GAV is higher of:
          1. Municipal value
          2. Fair rental value
          3. Standard rent
          4. Actual rent received
        
        For deemed-let property:
        - GAV is higher of:
          1. Municipal value
          2. Fair rental value
          3. Standard rent
        """
        if self.property_type == "self-occupied":
            return Money.zero()
        
        # Calculate higher of municipal value, fair rental value, and standard rent
        higher_of_three = max(
            self.municipal_value.amount,
            self.fair_rental_value.amount,
            self.standard_rent.amount
        )
        
        if self.property_type == "let-out":
            # For let-out, compare with actual rent
            return Money(max(higher_of_three, self.actual_rent.amount))
        else:
            # For deemed-let, use higher of three
            return Money(higher_of_three)
    
    def get_net_annual_value(self) -> Money:
        """
        Calculate Net Annual Value (NAV) of the property.
        
        NAV = GAV - Municipal taxes
        """
        return self.get_gross_annual_value().subtract(self.municipal_tax)
    
    def get_standard_deduction(self) -> Money:
        """
        Calculate standard deduction.
        
        Standard deduction is 30% of NAV.
        """
        return self.get_net_annual_value().percentage(Decimal('30'))
    
    def get_interest_deduction(self) -> Money:
        """
        Calculate interest deduction on home loan.
        
        For self-occupied property:
        - Maximum ₹2 lakh per year
        
        For let-out/deemed-let property:
        - No limit on interest deduction
        """
        if not self.loan_taken:
            return Money.zero()
        
        total_interest = self.interest_on_loan.add(self.pre_construction_interest)
        
        if self.property_type == "self-occupied":
            return total_interest.min(Money(Decimal('200000')))
        else:
            return total_interest
    
    def get_total_deductions(self) -> Money:
        """Get total deductions from house property income."""
        return (
            self.municipal_tax
            .add(self.get_standard_deduction())
            .add(self.get_interest_deduction())
            .add(self.other_deductions)
        )
    
    def get_income_from_house_property(self) -> Money:
        """
        Calculate income from house property.
        
        Income = NAV - Standard deduction - Interest deduction - Other deductions
        """
        return self.get_net_annual_value().subtract(self.get_total_deductions())
    
    def calculate_pre_construction_interest(self, current_year: int) -> Money:
        """
        Calculate pre-construction interest.
        
        Pre-construction interest is allowed in 5 equal installments
        starting from the year in which construction is completed.
        
        Args:
            current_year: Current financial year
            
        Returns:
            Money: Pre-construction interest for current year
        """
        if not self.loan_taken or not self.pre_construction_interest.is_positive():
            return Money.zero()
        
        if not self.construction_completed or not self.construction_year:
            return Money.zero()
        
        years_since_completion = current_year - self.construction_year
        
        if years_since_completion < 0 or years_since_completion >= 5:
            return Money.zero()
        
        # Divide pre-construction interest into 5 equal parts
        return self.pre_construction_interest.divide(5)
    
    def is_self_occupied(self) -> bool:
        """Check if property is self-occupied."""
        return self.property_type == "self-occupied"
    
    def is_let_out(self) -> bool:
        """Check if property is let-out."""
        return self.property_type == "let-out"
    
    def is_deemed_let(self) -> bool:
        """Check if property is deemed-let."""
        return self.property_type == "deemed-let"
    
    def get_property_type_description(self) -> str:
        """Get human-readable property type description."""
        if self.is_self_occupied():
            return "Self-occupied Property"
        elif self.is_let_out():
            return "Let-out Property"
        else:
            return "Deemed-let Property" 