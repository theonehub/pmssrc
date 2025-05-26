"""
Tax Regime Value Object
Immutable value object representing tax regime types and their properties
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any
from decimal import Decimal


class RegimeType(Enum):
    """Tax regime types available in Indian taxation"""
    OLD = "old"
    NEW = "new"


@dataclass(frozen=True)
class TaxRegime:
    """
    Tax regime value object ensuring immutability and business rules.
    
    Follows SOLID principles:
    - SRP: Only handles tax regime representation and rules
    - OCP: Can be extended with new regime types without modification
    - LSP: Can be substituted anywhere TaxRegime is expected
    - ISP: Provides only regime-related operations
    - DIP: Doesn't depend on concrete implementations
    """
    
    regime_type: RegimeType
    
    def __post_init__(self):
        """Validate tax regime on creation"""
        if not isinstance(self.regime_type, RegimeType):
            if isinstance(self.regime_type, str):
                try:
                    regime_type = RegimeType(self.regime_type.lower())
                    object.__setattr__(self, 'regime_type', regime_type)
                except ValueError:
                    raise ValueError(f"Invalid regime type: {self.regime_type}")
            else:
                raise ValueError("Regime type must be RegimeType enum or string")
    
    @classmethod
    def old_regime(cls) -> 'TaxRegime':
        """Create old regime instance"""
        return cls(RegimeType.OLD)
    
    @classmethod
    def new_regime(cls) -> 'TaxRegime':
        """Create new regime instance"""
        return cls(RegimeType.NEW)
    
    @classmethod
    def from_string(cls, regime_str: str) -> 'TaxRegime':
        """Create TaxRegime from string"""
        return cls(RegimeType(regime_str.lower()))
    
    def is_old_regime(self) -> bool:
        """Check if this is old tax regime"""
        return self.regime_type == RegimeType.OLD
    
    def is_new_regime(self) -> bool:
        """Check if this is new tax regime"""
        return self.regime_type == RegimeType.NEW
    
    def allows_deductions(self) -> bool:
        """
        Business rule: Check if regime allows deductions.
        Old regime allows most deductions, new regime has limited deductions.
        """
        return self.is_old_regime()
    
    def allows_section_80c(self) -> bool:
        """Check if regime allows Section 80C deductions"""
        return self.is_old_regime()
    
    def allows_section_80d(self) -> bool:
        """Check if regime allows Section 80D deductions"""
        return self.is_old_regime()
    
    def allows_hra_exemption(self) -> bool:
        """Check if regime allows HRA exemption"""
        return self.is_old_regime()
    
    def allows_standard_deduction(self) -> bool:
        """Check if regime allows standard deduction"""
        # Both regimes allow standard deduction but amounts may differ
        return True
    
    def get_standard_deduction_limit(self) -> Decimal:
        """Get standard deduction limit for the regime"""
        if self.is_old_regime():
            return Decimal('50000')  # Rs. 50,000 for old regime
        else:
            return Decimal('50000')  # Rs. 50,000 for new regime (as of current rules)
    
    def get_basic_exemption_limit(self) -> Decimal:
        """Get basic exemption limit for the regime"""
        if self.is_old_regime():
            return Decimal('250000')  # Rs. 2.5 lakhs for old regime
        else:
            return Decimal('300000')  # Rs. 3 lakhs for new regime
    
    def get_senior_citizen_exemption_limit(self) -> Decimal:
        """Get senior citizen exemption limit for the regime"""
        if self.is_old_regime():
            return Decimal('300000')  # Rs. 3 lakhs for old regime
        else:
            return Decimal('300000')  # Rs. 3 lakhs for new regime (same as basic in new regime)
    
    def get_super_senior_citizen_exemption_limit(self) -> Decimal:
        """Get super senior citizen exemption limit for the regime"""
        if self.is_old_regime():
            return Decimal('500000')  # Rs. 5 lakhs for old regime
        else:
            return Decimal('300000')  # Rs. 3 lakhs for new regime (same as basic in new regime)
    
    def get_tax_slabs(self) -> List[Dict[str, Any]]:
        """
        Get tax slabs for the regime.
        Returns list of dictionaries with 'min', 'max', and 'rate' keys.
        """
        if self.is_old_regime():
            return [
                {'min': Decimal('0'), 'max': Decimal('250000'), 'rate': Decimal('0')},
                {'min': Decimal('250000'), 'max': Decimal('500000'), 'rate': Decimal('5')},
                {'min': Decimal('500000'), 'max': Decimal('1000000'), 'rate': Decimal('20')},
                {'min': Decimal('1000000'), 'max': None, 'rate': Decimal('30')}
            ]
        else:
            return [
                {'min': Decimal('0'), 'max': Decimal('300000'), 'rate': Decimal('0')},
                {'min': Decimal('300000'), 'max': Decimal('600000'), 'rate': Decimal('5')},
                {'min': Decimal('600000'), 'max': Decimal('900000'), 'rate': Decimal('10')},
                {'min': Decimal('900000'), 'max': Decimal('1200000'), 'rate': Decimal('15')},
                {'min': Decimal('1200000'), 'max': Decimal('1500000'), 'rate': Decimal('20')},
                {'min': Decimal('1500000'), 'max': None, 'rate': Decimal('30')}
            ]
    
    def get_cess_rate(self) -> Decimal:
        """Get health and education cess rate (applicable to both regimes)"""
        return Decimal('4')  # 4% cess on tax amount
    
    def get_surcharge_slabs(self) -> List[Dict[str, Any]]:
        """
        Get surcharge slabs for the regime.
        Returns list of dictionaries with 'min', 'max', and 'rate' keys.
        """
        # Surcharge rates are same for both regimes
        return [
            {'min': Decimal('0'), 'max': Decimal('5000000'), 'rate': Decimal('0')},
            {'min': Decimal('5000000'), 'max': Decimal('10000000'), 'rate': Decimal('10')},
            {'min': Decimal('10000000'), 'max': Decimal('20000000'), 'rate': Decimal('15')},
            {'min': Decimal('20000000'), 'max': Decimal('50000000'), 'rate': Decimal('25')},
            {'min': Decimal('50000000'), 'max': None, 'rate': Decimal('37')}
        ]
    
    def supports_rebate_87a(self) -> bool:
        """Check if regime supports rebate under section 87A"""
        return True  # Both regimes support rebate 87A but with different limits
    
    def get_rebate_87a_limit(self) -> Decimal:
        """Get rebate 87A income limit"""
        if self.is_old_regime():
            return Decimal('500000')  # Rs. 5 lakhs for old regime
        else:
            return Decimal('700000')  # Rs. 7 lakhs for new regime
    
    def get_rebate_87a_amount(self) -> Decimal:
        """Get maximum rebate 87A amount"""
        if self.is_old_regime():
            return Decimal('12500')  # Rs. 12,500 for old regime
        else:
            return Decimal('25000')  # Rs. 25,000 for new regime
    
    def get_allowed_deduction_sections(self) -> List[str]:
        """Get list of allowed deduction sections"""
        if self.is_old_regime():
            return [
                '80C', '80CCC', '80CCD(1)', '80CCD(1B)', '80CCD(2)',
                '80D', '80DD', '80DDB', '80E', '80EE', '80EEA', '80EEB',
                '80G', '80GG', '80GGA', '80GGC', '80IA', '80IB', '80IC',
                '80ID', '80IE', '80JJA', '80JJAA', '80LA', '80P', '80QQB',
                '80RRB', '80TTA', '80TTB', '80U'
            ]
        else:
            # New regime allows very limited deductions
            return ['80CCD(2)', '80JJAA']  # Only employer contribution to NPS and employment generation
    
    def to_string(self) -> str:
        """Convert to string representation"""
        return self.regime_type.value
    
    def __str__(self) -> str:
        """String representation"""
        return f"{self.regime_type.value.title()} Regime"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"TaxRegime(regime_type={self.regime_type})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if isinstance(other, TaxRegime):
            return self.regime_type == other.regime_type
        elif isinstance(other, str):
            return self.regime_type.value == other.lower()
        elif isinstance(other, RegimeType):
            return self.regime_type == other
        return False
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash(self.regime_type) 