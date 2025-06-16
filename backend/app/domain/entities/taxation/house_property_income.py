"""
House Property Income Entity
Domain entity for handling income from house property
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType


class PropertyType(Enum):
    """Types of house property."""
    SELF_OCCUPIED = "Self-Occupied"
    LET_OUT = "Let-Out"
    DEEMED_LET_OUT = "Deemed Let-Out"


@dataclass
class HousePropertyIncome:
    """House property income calculation entity."""
    
    property_type: PropertyType
    annual_rent_received: Money = Money.zero()
    municipal_taxes_paid: Money = Money.zero()
    home_loan_interest: Money = Money.zero()
    pre_construction_interest: Money = Money.zero()
    fair_rental_value: Money = Money.zero()
    standard_rent: Money = Money.zero()
    
    def calculate_annual_value(self) -> Money:
        """
        Calculate annual value of property.
        
        Returns:
            Money: Annual value
        """
        if self.property_type == PropertyType.SELF_OCCUPIED:
            return Money.zero()
        
        elif self.property_type == PropertyType.LET_OUT:
            return self.annual_rent_received
        
        elif self.property_type == PropertyType.DEEMED_LET_OUT:
            # Annual value is higher of fair rental value and standard rent
            return self.fair_rental_value.max(self.standard_rent)
        
        return Money.zero()
    
    def calculate_net_annual_value(self) -> Money:
        """
        Calculate net annual value (annual value minus municipal taxes).
        
        Returns:
            Money: Net annual value
        """
        annual_value = self.calculate_annual_value()
        return annual_value.subtract(self.municipal_taxes_paid).max(Money.zero())
    
    def calculate_standard_deduction(self) -> Money:
        """
        Calculate standard deduction (30% of net annual value for let-out properties).
        
        Returns:
            Money: Standard deduction
        """
        if self.property_type == PropertyType.SELF_OCCUPIED:
            return Money.zero()
        
        net_annual_value = self.calculate_net_annual_value()
        return net_annual_value.percentage(30)  # 30% standard deduction
    
    def calculate_interest_deduction(self) -> Money:
        """
        Calculate home loan interest deduction.
        
        Returns:
            Money: Interest deduction
        """
        if self.property_type == PropertyType.SELF_OCCUPIED:
            # Maximum ₹2 lakh for self-occupied property
            max_limit = Money.from_int(200000)
            return self.home_loan_interest.min(max_limit)
        else:
            # No upper limit for let-out property
            return self.home_loan_interest
    
    def calculate_pre_construction_deduction(self) -> Money:
        """
        Calculate pre-construction interest deduction (1/5th over 5 years).
        
        Returns:
            Money: Pre-construction interest deduction
        """
        if self.pre_construction_interest.is_zero():
            return Money.zero()
        
        # Pre-construction interest is allowed as 1/5th over 5 years
        return self.pre_construction_interest.divide(5)
    
    def calculate_net_income_from_house_property(self, regime: TaxRegime) -> Money:
        """
        Calculate net income from house property.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Net income from house property (returns zero for losses)
        """
        net_annual_value = self.calculate_net_annual_value()
        standard_deduction = self.calculate_standard_deduction()
        interest_deduction = self.calculate_interest_deduction()
        pre_construction_deduction = self.calculate_pre_construction_deduction()
        
        total_deductions = (standard_deduction
                          .add(interest_deduction)
                          .add(pre_construction_deduction))
        
        # Income from house property can be negative (loss)
        # Since Money class doesn't allow negative amounts, we return zero for losses
        # The actual loss amount can be retrieved via get_house_property_breakdown
        if total_deductions.is_greater_than(net_annual_value):
            return Money.zero()  # Loss case - return zero
        else:
            return net_annual_value.subtract(total_deductions)
    
    def get_house_property_loss(self, regime: TaxRegime) -> Money:
        """
        Get house property loss amount if any.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Loss amount (zero if no loss)
        """
        net_annual_value = self.calculate_net_annual_value()
        standard_deduction = self.calculate_standard_deduction()
        interest_deduction = self.calculate_interest_deduction()
        pre_construction_deduction = self.calculate_pre_construction_deduction()
        
        total_deductions = (standard_deduction
                          .add(interest_deduction)
                          .add(pre_construction_deduction))
        
        if total_deductions.is_greater_than(net_annual_value):
            return total_deductions.subtract(net_annual_value)
        else:
            return Money.zero()
    
    # Properties for TaxCalculationService compatibility
    @property
    def actual_rent(self) -> Money:
        """Get actual rent for TaxCalculationService compatibility."""
        return self.annual_rent_received
    
    @property
    def municipal_tax(self) -> Money:
        """Get municipal tax for TaxCalculationService compatibility."""
        return self.municipal_taxes_paid
    
    @property
    def interest_on_loan(self) -> Money:
        """Get interest on loan for TaxCalculationService compatibility."""
        return self.home_loan_interest
    
    @property
    def other_deductions(self) -> Money:
        """Get other deductions for TaxCalculationService compatibility."""
        return Money.zero()  # Default to zero as this field doesn't exist in the taxation entity
    
    @property
    def municipal_value(self) -> Money:
        """Backward compatibility: Get municipal value (same as fair rental value)."""
        # Municipal value is typically the same as fair rental value in legacy systems
        return self.fair_rental_value
    
    def get_income_from_house_property(self) -> Money:
        """
        Calculate income from house property for TaxCalculationService.
        
        This method is used by TaxCalculationService.
        
        Returns:
            Money: Income from house property
        """
        from app.domain.value_objects.taxation.tax_regime import TaxRegime, TaxRegimeType
        # Use old regime as default for compatibility
        regime = TaxRegime(TaxRegimeType.OLD)
        return self.calculate_net_income_from_house_property(regime)

    def get_house_property_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """
        Get detailed breakdown of house property income calculation.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: Complete house property breakdown
        """
        annual_value = self.calculate_annual_value()
        net_annual_value = self.calculate_net_annual_value()
        standard_deduction = self.calculate_standard_deduction()
        interest_deduction = self.calculate_interest_deduction()
        pre_construction_deduction = self.calculate_pre_construction_deduction()
        net_income = self.calculate_net_income_from_house_property(regime)
        loss_amount = self.get_house_property_loss(regime)
        
        total_deductions = (standard_deduction
                          .add(interest_deduction)
                          .add(pre_construction_deduction))
        
        is_loss = loss_amount.is_positive()
        actual_net_income = -loss_amount.to_float() if is_loss else net_income.to_float()
        
        return {
            "property_type": self.property_type.value,
            "calculation_details": {
                "annual_rent_received": self.annual_rent_received.to_float(),
                "fair_rental_value": self.fair_rental_value.to_float(),
                "standard_rent": self.standard_rent.to_float(),
                "annual_value": annual_value.to_float(),
                "municipal_taxes_paid": self.municipal_taxes_paid.to_float(),
                "net_annual_value": net_annual_value.to_float()
            },
            "deductions": {
                "standard_deduction_30_percent": standard_deduction.to_float(),
                "home_loan_interest": interest_deduction.to_float(),
                "pre_construction_interest": pre_construction_deduction.to_float(),
                "total_deductions": total_deductions.to_float()
            },
            "net_income_from_house_property": actual_net_income,
            "is_loss": is_loss,
            "loss_amount": loss_amount.to_float() if is_loss else 0.0
        }


@dataclass
class MultipleHouseProperties:
    """Entity for handling multiple house properties."""
    
    properties: list[HousePropertyIncome]
    
    def calculate_total_house_property_income(self, regime: TaxRegime) -> Money:
        """
        Calculate total income from all house properties.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Total house property income
        """
        total_income = Money.zero()
        
        for property_income in self.properties:
            property_net_income = property_income.calculate_net_income_from_house_property(regime)
            total_income = total_income.add(property_net_income)
        
        return total_income
    
    def get_all_properties_breakdown(self, regime: TaxRegime) -> Dict[str, Any]:
        """
        Get breakdown of all properties.
        
        Args:
            regime: Tax regime
            
        Returns:
            Dict: All properties breakdown
        """
        properties_breakdown = []
        total_income = Money.zero()
        
        for i, property_income in enumerate(self.properties, 1):
            property_breakdown = property_income.get_house_property_breakdown(regime)
            property_breakdown["property_number"] = i
            properties_breakdown.append(property_breakdown)
            
            property_net_income = Money.from_float(property_breakdown["net_income_from_house_property"])
            total_income = total_income.add(property_net_income)
        
        return {
            "total_properties": len(self.properties),
            "properties_breakdown": properties_breakdown,
            "total_house_property_income": total_income.to_float(),
            "regime": regime.regime_type.value
        } 