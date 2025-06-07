"""
Reimbursement Amount Value Object
Immutable representation of monetary amounts with currency
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Union


@dataclass(frozen=True)
class ReimbursementAmount:
    """
    Reimbursement amount value object ensuring immutability and validation.
    
    Follows SOLID principles:
    - SRP: Only handles monetary amount representation and validation
    - OCP: Can be extended without modification
    - LSP: Can be substituted anywhere ReimbursementAmount is expected
    - ISP: Provides only amount-related operations
    - DIP: Doesn't depend on concrete implementations
    """
    
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        """Validate amount on creation"""
        if not isinstance(self.amount, Decimal):
            raise ValueError("Amount must be a Decimal")
        
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        
        if self.amount > Decimal('9999999.99'):
            raise ValueError("Amount cannot exceed ₹99,99,999.99")
        
        # Validate currency
        valid_currencies = ["INR", "USD", "EUR", "GBP"]
        if self.currency not in valid_currencies:
            raise ValueError(f"Currency must be one of: {', '.join(valid_currencies)}")
        
        # Round to 2 decimal places for currency
        rounded_amount = self.amount.quantize(Decimal('0.01'))
        object.__setattr__(self, 'amount', rounded_amount)
    
    @classmethod
    def from_float(cls, amount: float, currency: str = "INR") -> 'ReimbursementAmount':
        """Create ReimbursementAmount from float"""
        return cls(Decimal(str(amount)), currency)
    
    @classmethod
    def from_string(cls, amount: str, currency: str = "INR") -> 'ReimbursementAmount':
        """Create ReimbursementAmount from string"""
        return cls(Decimal(amount), currency)
    
    @classmethod
    def zero(cls, currency: str = "INR") -> 'ReimbursementAmount':
        """Create zero amount"""
        return cls(Decimal('0'), currency)
    
    def add(self, other: 'ReimbursementAmount') -> 'ReimbursementAmount':
        """Add two amounts (must have same currency)"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add amounts with different currencies: {self.currency} and {other.currency}")
        
        return ReimbursementAmount(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'ReimbursementAmount') -> 'ReimbursementAmount':
        """Subtract two amounts (must have same currency)"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract amounts with different currencies: {self.currency} and {other.currency}")
        
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Result cannot be negative")
        
        return ReimbursementAmount(result_amount, self.currency)
    
    def multiply(self, factor: Union[Decimal, float, int]) -> 'ReimbursementAmount':
        """Multiply amount by a factor"""
        if isinstance(factor, (float, int)):
            factor = Decimal(str(factor))
        
        if factor < 0:
            raise ValueError("Factor cannot be negative")
        
        return ReimbursementAmount(self.amount * factor, self.currency)
    
    def divide(self, divisor: Union[Decimal, float, int]) -> 'ReimbursementAmount':
        """Divide amount by a divisor"""
        if isinstance(divisor, (float, int)):
            divisor = Decimal(str(divisor))
        
        if divisor <= 0:
            raise ValueError("Divisor must be positive")
        
        return ReimbursementAmount(self.amount / divisor, self.currency)
    
    def is_greater_than(self, other: Union['ReimbursementAmount', Decimal]) -> bool:
        """Check if this amount is greater than another"""
        if isinstance(other, ReimbursementAmount):
            return self.amount > other.amount
        elif isinstance(other, Decimal):
            return self.amount > other
        else:
            raise TypeError(f"Cannot compare ReimbursementAmount with {type(other)}")
    
    def is_less_than(self, other: Union['ReimbursementAmount', Decimal]) -> bool:
        """Check if this amount is less than another"""
        if isinstance(other, ReimbursementAmount):
            return self.amount < other.amount
        elif isinstance(other, Decimal):
            return self.amount < other
        else:
            raise TypeError(f"Cannot compare ReimbursementAmount with {type(other)}")
    
    def is_equal_to(self, other: Union['ReimbursementAmount', Decimal]) -> bool:
        """Check if this amount is equal to another"""
        if isinstance(other, ReimbursementAmount):
            return self.currency == other.currency and self.amount == other.amount
        elif isinstance(other, Decimal):
            return self.amount == other
        else:
            raise TypeError(f"Cannot compare ReimbursementAmount with {type(other)}")
    
    def is_zero(self) -> bool:
        """Check if amount is zero"""
        return self.amount == Decimal('0')
    
    def to_float(self) -> float:
        """Convert to float representation"""
        return float(self.amount)
    
    def to_string(self) -> str:
        """Convert to string representation"""
        return f"{self.currency} {self.amount}"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "amount": float(self.amount),
            "currency": self.currency
        }
    
    def __str__(self) -> str:
        """String representation"""
        currency_symbols = {
            "INR": "₹",
            "USD": "$",
            "EUR": "€",
            "GBP": "£"
        }
        symbol = currency_symbols.get(self.currency, self.currency)
        return f"{symbol}{self.amount}"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"ReimbursementAmount({self.amount}, '{self.currency}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if isinstance(other, ReimbursementAmount):
            return self.amount == other.amount and self.currency == other.currency
        return False
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash((self.amount, self.currency))
    
    def __lt__(self, other: 'ReimbursementAmount') -> bool:
        """Less than comparison for sorting"""
        if not isinstance(other, ReimbursementAmount):
            raise TypeError("Cannot compare ReimbursementAmount with non-ReimbursementAmount")
        
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare amounts with different currencies: {self.currency} and {other.currency}")
        
        return self.amount < other.amount
    
    def __le__(self, other: 'ReimbursementAmount') -> bool:
        """Less than or equal comparison"""
        return self == other or self < other
    
    def __gt__(self, other: 'ReimbursementAmount') -> bool:
        """Greater than comparison"""
        return not self <= other
    
    def __ge__(self, other: 'ReimbursementAmount') -> bool:
        """Greater than or equal comparison"""
        return self == other or self > other 