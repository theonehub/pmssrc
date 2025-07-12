"""
Tax Regime Value Object
Immutable value object for Indian tax regime handling (old vs new regime)
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import List, Dict, Any

from app.domain.value_objects.money import Money


class TaxRegimeType(Enum):
    """Tax regime types in India."""
    OLD = "old"
    NEW = "new"


@dataclass(frozen=True)
class TaxRegime:
    """
    Tax regime value object with specific rules and validations.
    
    Handles differences between old and new tax regimes in India.
    """
    
    regime_type: TaxRegimeType
    
    def allows_deductions(self) -> bool:
        """Check if this regime allows traditional deductions."""
        return self.regime_type == TaxRegimeType.OLD
    
    def get_standard_deduction(self) -> Money:
        if self.regime_type == TaxRegimeType.NEW:
            return Money.from_int(75000)  # ₹75,000 for new regime
        else:
            return Money.from_int(50000)  # ₹50,000 for old regime
    
    def get_basic_exemption_limit(self, age: int) -> Money:
        """
        Get basic exemption limit based on taxpayer age.
        
        Args:
            age: Taxpayer's age in years
            
        Returns:
            Money: Basic exemption limit
        """
        if self.regime_type == TaxRegimeType.NEW:
            # New regime has flat ₹3 lakh exemption regardless of age
            return Money.from_int(300000)
        
        # Old regime age-based exemptions
        if age < 60:
            return Money.from_int(250000)  # ₹2.5 lakh
        elif age < 80:
            return Money.from_int(300000)  # ₹3 lakh (senior citizen)
        else:
            return Money.from_int(500000)  # ₹5 lakh (super senior citizen)
    
    def get_tax_slabs(self, age: int) -> List[Dict[str, Any]]:
        """
        Get tax slabs based on regime and age.
        
        Args:
            age: Taxpayer's age in years
            
        Returns:
            List[Dict]: Tax slabs with min, max, and rate
        """
        if self.regime_type == TaxRegimeType.NEW:
            return [
                {"min": Decimal('0'), "max": Decimal('300000'), "rate": Decimal('0')},
                {"min": Decimal('300000'), "max": Decimal('700000'), "rate": Decimal('5')},
                {"min": Decimal('700000'), "max": Decimal('1000000'), "rate": Decimal('10')},
                {"min": Decimal('1000000'), "max": Decimal('1200000'), "rate": Decimal('15')},
                {"min": Decimal('1200000'), "max": Decimal('1500000'), "rate": Decimal('20')},
                {"min": Decimal('1500000'), "max": None, "rate": Decimal('30')}
            ]
        else:  # OLD regime
            basic_exemption = self.get_basic_exemption_limit(age)
            return [
                {"min": Decimal('0'), "max": basic_exemption.amount, "rate": Decimal('0')},
                {"min": basic_exemption.amount, "max": Decimal('500000'), "rate": Decimal('5')},
                {"min": Decimal('500000'), "max": Decimal('1000000'), "rate": Decimal('20')},
                {"min": Decimal('1000000'), "max": None, "rate": Decimal('30')}
            ]
    
    def get_rebate_87a_limit(self) -> Money:
        """Get income limit for Section 87A rebate."""
        if self.regime_type == TaxRegimeType.NEW:
            return Money.from_int(700000)  # ₹7 lakh in new regime
        else:
            return Money.from_int(500000)  # ₹5 lakh in old regime
    
    def get_max_rebate_87a(self) -> Money:
        """Get maximum rebate amount under Section 87A."""
        if self.regime_type == TaxRegimeType.NEW:
            return Money.from_int(25000)  # ₹25,000 in new regime
        else:
            return Money.from_int(12500)  # ₹12,500 in old regime
    
    def supports_section_80c(self) -> bool:
        """Check if Section 80C deductions are allowed."""
        return self.regime_type == TaxRegimeType.OLD
    
    def supports_section_80d(self) -> bool:
        """Check if Section 80D deductions are allowed."""
        return self.regime_type == TaxRegimeType.OLD
    
    def supports_hra_exemption(self) -> bool:
        """Check if HRA exemption is allowed."""
        return self.regime_type == TaxRegimeType.OLD
    
    def get_regime_description(self) -> str:
        """Get human-readable description of the regime."""
        if self.regime_type == TaxRegimeType.NEW:
            return "New Tax Regime (Lower rates, no deductions)"
        else:
            return "Old Tax Regime (Higher rates, with deductions)"
    
    def get_key_features(self) -> List[str]:
        """Get key features of this regime."""
        if self.regime_type == TaxRegimeType.NEW:
            return [
                "Lower tax rates",
                "No deductions under sections 80C, 80D, etc.",
                "No HRA exemption (except standard deduction)",
                "Rebate up to ₹25,000 for income up to ₹7 lakh",
                "Simplified tax structure"
            ]
        else:
            return [
                "Traditional tax rates",
                "All deductions available (80C, 80D, etc.)",
                "HRA exemption available",
                "Rebate up to ₹12,500 for income up to ₹5 lakh",
                "Complex deduction calculations"
            ]
    
    @classmethod
    def old_regime(cls) -> 'TaxRegime':
        """Create old tax regime instance."""
        return cls(TaxRegimeType.OLD)
    
    @classmethod
    def new_regime(cls) -> 'TaxRegime':
        """Create new tax regime instance."""
        return cls(TaxRegimeType.NEW)
    
    @classmethod
    def from_string(cls, regime_str: str) -> 'TaxRegime':
        """
        Create regime from string representation.
        
        Args:
            regime_str: "old", "new", "OLD", "NEW", etc.
            
        Returns:
            TaxRegime: Corresponding regime instance
        """
        regime_str = regime_str.strip().lower()
        if regime_str == "old":
            return cls.old_regime()
        elif regime_str == "new":
            return cls.new_regime()
        else:
            raise ValueError(f"Invalid tax regime: '{regime_str}'. Use 'old' or 'new'")
    
    def __str__(self) -> str:
        """String representation."""
        return self.regime_type.value.title()
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"TaxRegime({self.regime_type.value})" 