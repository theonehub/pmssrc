"""
Money Value Object
Immutable value object representing monetary amounts with currency
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Union


@dataclass(frozen=True)
class Money:
    """
    Money value object ensuring immutability and validation.
    
    Follows SOLID principles:
    - SRP: Only handles money representation and operations
    - OCP: Can be extended without modification
    - LSP: Can be substituted anywhere Money is expected
    - ISP: Provides only money-related operations
    - DIP: Doesn't depend on concrete implementations
    """
    
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        """Validate money object on creation"""
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        
        if not self.currency:
            raise ValueError("Currency is required")
        
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3 characters (ISO 4217)")
        
        # Round to 2 decimal places for currency precision
        rounded_amount = self.amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        object.__setattr__(self, 'amount', rounded_amount)
    
    @classmethod
    def zero(cls, currency: str = "INR") -> 'Money':
        """Create zero money amount"""
        return cls(Decimal('0'), currency)
    
    @classmethod
    def from_float(cls, amount: float, currency: str = "INR") -> 'Money':
        """Create Money from float (use with caution due to float precision)"""
        return cls(Decimal(str(amount)), currency)
    
    @classmethod
    def from_int(cls, amount: int, currency: str = "INR") -> 'Money':
        """Create Money from integer"""
        return cls(Decimal(amount), currency)
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money amounts"""
        self._validate_same_currency(other)
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract money amounts"""
        self._validate_same_currency(other)
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Result cannot be negative")
        return Money(result_amount, self.currency)
    
    def multiply(self, factor: Union[Decimal, int, float]) -> 'Money':
        """Multiply money by a factor"""
        if isinstance(factor, (int, float)):
            factor = Decimal(str(factor))
        
        if factor < 0:
            raise ValueError("Factor cannot be negative")
        
        return Money(self.amount * factor, self.currency)
    
    def divide(self, divisor: Union[Decimal, int, float]) -> 'Money':
        """Divide money by a divisor"""
        if isinstance(divisor, (int, float)):
            divisor = Decimal(str(divisor))
        
        if divisor <= 0:
            raise ValueError("Divisor must be positive")
        
        return Money(self.amount / divisor, self.currency)
    
    def percentage(self, percent: Union[Decimal, int, float]) -> 'Money':
        """Calculate percentage of money amount"""
        if isinstance(percent, (int, float)):
            percent = Decimal(str(percent))
        
        if percent < 0:
            raise ValueError("Percentage cannot be negative")
        
        return Money(self.amount * (percent / Decimal('100')), self.currency)
    
    def is_zero(self) -> bool:
        """Check if amount is zero"""
        return self.amount == Decimal('0')
    
    def is_positive(self) -> bool:
        """Check if amount is positive"""
        return self.amount > Decimal('0')
    
    def compare_to(self, other: 'Money') -> int:
        """Compare two money amounts. Returns -1, 0, or 1"""
        self._validate_same_currency(other)
        
        if self.amount < other.amount:
            return -1
        elif self.amount > other.amount:
            return 1
        else:
            return 0
    
    def max(self, other: 'Money') -> 'Money':
        """Return the maximum of two money amounts"""
        self._validate_same_currency(other)
        return self if self.amount >= other.amount else other
    
    def min(self, other: 'Money') -> 'Money':
        """Return the minimum of two money amounts"""
        self._validate_same_currency(other)
        return self if self.amount <= other.amount else other
    
    def to_float(self) -> float:
        """Convert to float (use with caution due to precision loss)"""
        return float(self.amount)
    
    def to_int(self) -> int:
        """Convert to integer (truncates decimal part)"""
        return int(self.amount)
    
    def format(self, include_currency: bool = True) -> str:
        """Format money for display"""
        formatted_amount = f"{self.amount:,.2f}"
        if include_currency:
            return f"{formatted_amount} {self.currency}"
        return formatted_amount
    
    def _validate_same_currency(self, other: 'Money'):
        """Validate that two money objects have the same currency"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot operate on different currencies: {self.currency} and {other.currency}")
    
    def __str__(self) -> str:
        """String representation"""
        return self.format()
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Money(amount={self.amount}, currency='{self.currency}')"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other: 'Money') -> bool:
        """Less than comparison"""
        self._validate_same_currency(other)
        return self.amount < other.amount
    
    def __le__(self, other: 'Money') -> bool:
        """Less than or equal comparison"""
        self._validate_same_currency(other)
        return self.amount <= other.amount
    
    def __gt__(self, other: 'Money') -> bool:
        """Greater than comparison"""
        self._validate_same_currency(other)
        return self.amount > other.amount
    
    def __ge__(self, other: 'Money') -> bool:
        """Greater than or equal comparison"""
        self._validate_same_currency(other)
        return self.amount >= other.amount
    
    def __add__(self, other: 'Money') -> 'Money':
        """Addition operator"""
        return self.add(other)
    
    def __sub__(self, other: 'Money') -> 'Money':
        """Subtraction operator"""
        return self.subtract(other)
    
    def __mul__(self, factor: Union[Decimal, int, float]) -> 'Money':
        """Multiplication operator"""
        return self.multiply(factor)
    
    def __truediv__(self, divisor: Union[Decimal, int, float]) -> 'Money':
        """Division operator"""
        return self.divide(divisor)
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries"""
        return hash((self.amount, self.currency)) 