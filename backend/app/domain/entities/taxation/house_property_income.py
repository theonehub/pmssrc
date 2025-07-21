"""
House Property Income Entity
Domain entity for handling income from house property
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_regime import TaxRegime, TaxRegimeType
from app.utils.logger import get_logger

logger = get_logger(__name__)

class PropertyType(Enum):
    """Types of house property."""
    SELF_OCCUPIED = "Self-Occupied"
    LET_OUT = "Let-Out"


@dataclass
class HousePropertyIncome:
    """House property income calculation entity."""
    
    property_type: PropertyType
    address: str = ""
    annual_rent_received: Money = Money.zero()
    municipal_taxes_paid: Money = Money.zero()
    home_loan_interest: Money = Money.zero()
    pre_construction_interest: Money = Money.zero()
    
    def calculate_annual_rent_received(self) -> Money:
        """
        Calculate annual rent received.
        
        Returns:
            Money: Annual rent received
        """
        
        if self.property_type == PropertyType.SELF_OCCUPIED:
            return Money.zero()
        
        elif self.property_type == PropertyType.LET_OUT:
            return self.annual_rent_received
        
        return Money.zero()
    
    def calculate_net_annual_income_after_taxes(self) -> Money:
        """
        Calculate net annual value (annual value minus municipal taxes).
        
        Returns:
            Money: Net annual value
        """
        annual_value = self.calculate_annual_rent_received()
        return annual_value.subtract(self.municipal_taxes_paid).max(Money.zero())
    
    def calculate_standard_deduction(self) -> Money:
        """
        Calculate standard deduction (30% of net annual value for let-out properties).
        
        Returns:
            Money: Standard deduction
        """
        if self.property_type == PropertyType.SELF_OCCUPIED:
            return Money.zero()
        
        net_annual_value = self.calculate_net_annual_income_after_taxes()
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
    
    def calculate_net_income_from_house_property(self, regime: TaxRegime, summary_data: Dict[str, Any] = None) -> Money:
        """
        Calculate net income from house property.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Net income from house property (returns zero for losses)
        """
        if summary_data:
            summary_data['calculate_net_income_from_house_property'] = True
            summary_data['regime'] = regime.regime_type.value
            summary_data['property_type'] = self.property_type.value
            summary_data['annual_rent_received'] = self.annual_rent_received
            summary_data['municipal_taxes_paid'] = self.municipal_taxes_paid
            summary_data['home_loan_interest'] = self.home_loan_interest
            summary_data['pre_construction_interest'] = self.pre_construction_interest
            

        net_annual_value = self.calculate_net_annual_income_after_taxes()
        standard_deduction = self.calculate_standard_deduction()
        interest_deduction = self.calculate_interest_deduction()
        pre_construction_deduction = self.calculate_pre_construction_deduction()
        
        total_deductions = (standard_deduction
                          .add(interest_deduction)
                          .add(pre_construction_deduction))
        if summary_data:
            summary_data['interest_deduction(2Lakh[Self-Occupied], No Limit[Let-Out])'] = interest_deduction
            summary_data['pre_construction_deduction(1/5th over 5 years)'] = pre_construction_deduction
            summary_data['annual_rent_received_after_taxes'] = net_annual_value
            summary_data['standard_deduction(30%)'] = standard_deduction
        
        # Income from house property can be negative (loss)
        # Since Money class doesn't allow negative amounts, we return zero for losses
        # The actual loss amount can be retrieved via get_house_property_breakdown
        if total_deductions.is_greater_than(net_annual_value):
            if summary_data:
                summary_data['total_deductions'] = total_deductions
                summary_data['is_loss'] = True
                summary_data['net_income_from_house_property'] = Money.zero()
            retval = Money.zero()  # Loss case - return zero
        else:
            retval  = net_annual_value.subtract(total_deductions)
            if summary_data:
                summary_data['is_loss'] = False
                summary_data['net_income_from_house_property'] = retval

        return retval
    
    def get_house_property_loss(self, regime: TaxRegime) -> Money:
        """
        Get house property loss amount if any.
        
        Args:
            regime: Tax regime
            
        Returns:
            Money: Loss amount (zero if no loss)
        """
        net_annual_value = self.calculate_net_annual_income_after_taxes()
        standard_deduction = self.calculate_standard_deduction()
        interest_deduction = self.calculate_interest_deduction()
        pre_construction_deduction = self.calculate_pre_construction_deduction()
        
        total_deductions = (standard_deduction
                          .add(interest_deduction)
                          .add(pre_construction_deduction))
        
        if total_deductions.is_greater_than(net_annual_value):
            loss = total_deductions.subtract(net_annual_value)
            logger.info(f"HPI: Total deductions are greater than net annual value, loss: {loss}")
            return loss
        else:
            logger.info(f"HPI: Total deductions are less than net annual value, returning zero")
            return Money.zero()
    

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
        """Backward compatibility: Get municipal value (same as annual rent received)."""
        # Municipal value is typically the same as annual rent received for let-out properties
        return self.annual_rent_received
    
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
        annual_value = self.calculate_annual_rent_received()
        net_annual_value = self.calculate_net_annual_income_after_taxes()
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