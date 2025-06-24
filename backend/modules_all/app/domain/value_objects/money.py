"""
Money Value Object
Immutable money value object with proper validation for Indian currency
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Union


@dataclass(frozen=True)
class Money:
    """
    Immutable money value object with proper validation for Indian currency.
    
    Handles all monetary calculations with proper precision and validation.
    """
    
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        """Validate money after initialization."""
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))
        
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        
        if self.currency != "INR":
            raise ValueError("Only INR currency supported")
        
        # Round to 2 decimal places for currency
        rounded_amount = self.amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        object.__setattr__(self, 'amount', rounded_amount)
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money amounts."""
        self._validate_currency(other)
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract two money amounts."""
        self._validate_currency(other)
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Cannot subtract to negative amount")
        return Money(result, self.currency)
    
    def multiply(self, factor: Union[Decimal, float, int]) -> 'Money':
        """Multiply money by a factor."""
        if not isinstance(factor, Decimal):
            factor = Decimal(str(factor))
        return Money(self.amount * factor, self.currency)
    
    def divide(self, divisor: Union[Decimal, float, int]) -> 'Money':
        """Divide money by a divisor."""
        if not isinstance(divisor, Decimal):
            divisor = Decimal(str(divisor))
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / divisor, self.currency)
    
    def percentage(self, percent: Union[Decimal, float, int]) -> 'Money':
        """Calculate percentage of money amount."""
        if not isinstance(percent, Decimal):
            percent = Decimal(str(percent))
        return Money((self.amount * percent) / Decimal('100'), self.currency)
    
    def min(self, other: 'Money') -> 'Money':
        """Return minimum of two money amounts."""
        self._validate_currency(other)
        return Money(min(self.amount, other.amount), self.currency)
    
    def max(self, other: 'Money') -> 'Money':
        """Return maximum of two money amounts."""
        self._validate_currency(other)
        return Money(max(self.amount, other.amount), self.currency)
    
    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self.amount == 0
    
    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self.amount > 0
    
    def is_greater_than(self, other: 'Money') -> bool:
        """Check if this amount is greater than other."""
        self._validate_currency(other)
        return self.amount > other.amount
    
    def is_less_than(self, other: 'Money') -> bool:
        """Check if this amount is less than other."""
        self._validate_currency(other)
        return self.amount < other.amount
    
    def is_equal_to(self, other: 'Money') -> bool:
        """Check if this amount equals other."""
        self._validate_currency(other)
        return self.amount == other.amount
    
    def _validate_currency(self, other: 'Money') -> None:
        """Validate currency compatibility."""
        if self.currency != other.currency:
            raise ValueError(f"Cannot operate on different currencies: {self.currency} vs {other.currency}")
    
    @classmethod
    def zero(cls) -> 'Money':
        """Create zero money amount."""
        return cls(Decimal('0'))
    
    @classmethod
    def from_decimal(cls, amount: Decimal) -> 'Money':
        """Create money from decimal value."""
        return cls(amount)
    
    @classmethod
    def from_float(cls, amount: float) -> 'Money':
        """Create money from float value."""
        return cls(Decimal(str(amount)))
    
    @classmethod
    def from_int(cls, amount: int) -> 'Money':
        """Create money from integer value."""
        return cls(Decimal(str(amount)))
    
    @classmethod
    def from_string(cls, amount: str) -> 'Money':
        """Create money from string value."""
        return cls(Decimal(amount))
    
    def to_float(self) -> float:
        """Convert to float (use with caution for display only)."""
        return float(self.amount)
    
    def to_int(self) -> int:
        """Convert to integer (rounded)."""
        return int(self.amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    
    def format_indian(self) -> str:
        """Format in Indian number system (lakhs, crores)."""
        amount = int(self.amount)
        
        if amount >= 10000000:  # 1 crore
            crores = amount // 10000000
            lakhs = (amount % 10000000) // 100000
            if lakhs > 0:
                return f"₹{crores},{lakhs:02d},00,000"
            else:
                return f"₹{crores} crore"
        elif amount >= 100000:  # 1 lakh
            lakhs = amount // 100000
            thousands = (amount % 100000) // 1000
            if thousands > 0:
                return f"₹{lakhs},{thousands:02d},000"
            else:
                return f"₹{lakhs} lakh"
        elif amount >= 1000:  # 1 thousand
            return f"₹{amount:,}"
        else:
            return f"₹{amount}"
    
    def __str__(self) -> str:
        """String representation."""
        return f"₹{self.amount:,.2f}"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"Money({self.amount}, {self.currency})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency
    
    def __lt__(self, other) -> bool:
        """Less than comparison."""
        if not isinstance(other, Money):
            return NotImplemented
        self._validate_currency(other)
        return self.amount < other.amount
    
    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, Money):
            return NotImplemented
        self._validate_currency(other)
        return self.amount <= other.amount
    
    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        if not isinstance(other, Money):
            return NotImplemented
        self._validate_currency(other)
        return self.amount > other.amount
    
    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, Money):
            return NotImplemented
        self._validate_currency(other)
        return self.amount >= other.amount
    
    def __add__(self, other) -> 'Money':
        """Addition operator (+)."""
        if not isinstance(other, Money):
            return NotImplemented
        return self.add(other)
    
    def __sub__(self, other) -> 'Money':
        """Subtraction operator (-)."""
        if not isinstance(other, Money):
            return NotImplemented
        return self.subtract(other)
    
    def __mul__(self, other) -> 'Money':
        """Multiplication operator (*)."""
        if isinstance(other, Money):
            return NotImplemented  # Cannot multiply money by money
        return self.multiply(other)
    
    def __rmul__(self, other) -> 'Money':
        """Reverse multiplication operator (*)."""
        return self.multiply(other)
    
    def __truediv__(self, other) -> 'Money':
        """Division operator (/)."""
        if isinstance(other, Money):
            return NotImplemented  # Cannot divide money by money
        return self.divide(other)
    
    def __neg__(self) -> 'Money':
        """Negation operator (-)."""
        # Since Money cannot be negative, this should raise an error
        raise ValueError("Money cannot be negative")
    
    def __abs__(self) -> 'Money':
        """Absolute value operator."""
        return self  # Money is always positive 