"""
Reimbursement Amount Value Object
Immutable representation of monetary amounts for reimbursements
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class ReimbursementAmount:
    """
    Value object representing a reimbursement amount.
    
    Follows SOLID principles:
    - SRP: Only represents monetary amount data
    - OCP: Extensible through composition
    - LSP: Maintains value object contracts
    - ISP: Focused interface for amounts
    - DIP: No dependencies on external systems
    """
    
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        """Validate reimbursement amount data"""
        if not isinstance(self.amount, Decimal):
            if isinstance(self.amount, (int, float, str)):
                object.__setattr__(self, 'amount', Decimal(str(self.amount)))
            else:
                raise ValueError("Amount must be a valid number")
        
        if self.amount < 0:
            raise ValueError("Reimbursement amount cannot be negative")
        
        if self.amount > Decimal('9999999.99'):
            raise ValueError("Reimbursement amount cannot exceed ₹99,99,999.99")
        
        # Round to 2 decimal places
        rounded_amount = self.amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        object.__setattr__(self, 'amount', rounded_amount)
        
        # Validate currency
        if not self.currency or self.currency.strip() == "":
            raise ValueError("Currency cannot be empty")
        
        object.__setattr__(self, 'currency', self.currency.upper().strip())
    
    @classmethod
    def from_float(cls, amount: float, currency: str = "INR") -> 'ReimbursementAmount':
        """Create from float value"""
        return cls(Decimal(str(amount)), currency)
    
    @classmethod
    def from_string(cls, amount: str, currency: str = "INR") -> 'ReimbursementAmount':
        """Create from string value"""
        # Remove currency symbols and commas
        cleaned_amount = amount.replace('₹', '').replace(',', '').strip()
        return cls(Decimal(cleaned_amount), currency)
    
    @classmethod
    def zero(cls, currency: str = "INR") -> 'ReimbursementAmount':
        """Create zero amount"""
        return cls(Decimal('0'), currency)
    
    def add(self, other: 'ReimbursementAmount') -> 'ReimbursementAmount':
        """Add two amounts"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        
        return ReimbursementAmount(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'ReimbursementAmount') -> 'ReimbursementAmount':
        """Subtract two amounts"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract different currencies: {self.currency} and {other.currency}")
        
        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Result cannot be negative")
        
        return ReimbursementAmount(result_amount, self.currency)
    
    def multiply(self, factor: Decimal) -> 'ReimbursementAmount':
        """Multiply amount by a factor"""
        if factor < 0:
            raise ValueError("Factor cannot be negative")
        
        return ReimbursementAmount(self.amount * factor, self.currency)
    
    def is_zero(self) -> bool:
        """Check if amount is zero"""
        return self.amount == Decimal('0')
    
    def is_greater_than(self, other: 'ReimbursementAmount') -> bool:
        """Check if this amount is greater than another"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare different currencies: {self.currency} and {other.currency}")
        
        return self.amount > other.amount
    
    def is_less_than(self, other: 'ReimbursementAmount') -> bool:
        """Check if this amount is less than another"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare different currencies: {self.currency} and {other.currency}")
        
        return self.amount < other.amount
    
    def is_equal_to(self, other: 'ReimbursementAmount') -> bool:
        """Check if this amount is equal to another"""
        return self.currency == other.currency and self.amount == other.amount
    
    def get_formatted_amount(self) -> str:
        """Get formatted amount with currency symbol"""
        if self.currency == "INR":
            return f"₹{self.amount:,.2f}"
        else:
            return f"{self.currency} {self.amount:,.2f}"
    
    def get_amount_in_words(self) -> str:
        """Get amount in words (Indian format)"""
        # This is a simplified version - in production, you'd use a proper library
        amount_str = str(self.amount)
        integer_part, decimal_part = amount_str.split('.') if '.' in amount_str else (amount_str, '00')
        
        # Basic conversion for demonstration
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        def convert_hundreds(num):
            result = ''
            if num >= 100:
                result += ones[num // 100] + ' Hundred '
                num %= 100
            if num >= 20:
                result += tens[num // 10] + ' '
                num %= 10
            elif num >= 10:
                result += teens[num - 10] + ' '
                num = 0
            if num > 0:
                result += ones[num] + ' '
            return result.strip()
        
        # Convert integer part
        num = int(integer_part)
        if num == 0:
            words = 'Zero'
        else:
            words = convert_hundreds(num)
        
        # Add currency
        if self.currency == "INR":
            words += ' Rupees'
            if int(decimal_part) > 0:
                words += ' and ' + convert_hundreds(int(decimal_part)) + ' Paise'
        else:
            words += f' {self.currency}'
        
        return words + ' Only'
    
    def to_float(self) -> float:
        """Convert to float (use with caution for calculations)"""
        return float(self.amount)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "amount": float(self.amount),
            "currency": self.currency,
            "formatted": self.get_formatted_amount()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ReimbursementAmount':
        """Create from dictionary"""
        return cls(
            amount=Decimal(str(data["amount"])),
            currency=data.get("currency", "INR")
        )
    
    def __str__(self) -> str:
        """String representation"""
        return self.get_formatted_amount()
    
    def __repr__(self) -> str:
        """Representation"""
        return f"ReimbursementAmount(amount={self.amount}, currency='{self.currency}')" 