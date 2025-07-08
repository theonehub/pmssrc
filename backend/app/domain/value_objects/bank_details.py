"""
Bank Details Value Object
Common value object for bank account information
"""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class BankDetails:
    """
    Value object for bank account details.
    
    Follows SOLID principles:
    - SRP: Only handles bank account information
    - OCP: Can be extended with new bank-related fields
    - LSP: Can be substituted anywhere BankDetails is expected
    - ISP: Focused interface for bank data
    - DIP: Doesn't depend on concrete implementations
    """
    
    account_number: str
    bank_name: str
    ifsc_code: str
    account_holder_name: str
    branch_name: Optional[str] = None
    branch_address: Optional[str] = None
    account_type: Optional[str] = None  # Savings, Current, etc.
    
    def __post_init__(self):
        """Validate bank details after initialization"""
        self._validate_account_number()
        self._validate_bank_name()
        self._validate_ifsc_code()
        self._validate_account_holder_name()
        if self.account_type:
            self._validate_account_type()
    
    def _validate_account_number(self) -> None:
        """Validate account number format"""
        if not self.account_number or not self.account_number.strip():
            raise ValueError("Account number is required")
        
        # Remove spaces and check if it's alphanumeric
        clean_account = re.sub(r'\s+', '', self.account_number)
        if not re.match(r'^[A-Za-z0-9]+$', clean_account):
            raise ValueError("Account number must contain only letters and numbers")
        
        # Check length (typically 9-18 digits for Indian banks)
        if len(clean_account) < 9 or len(clean_account) > 18:
            raise ValueError("Account number must be between 9 and 18 characters")
    
    def _validate_bank_name(self) -> None:
        """Validate bank name"""
        if not self.bank_name or not self.bank_name.strip():
            raise ValueError("Bank name is required")
        
        if len(self.bank_name.strip()) < 2:
            raise ValueError("Bank name must be at least 2 characters long")
    
    def _validate_ifsc_code(self) -> None:
        """Validate IFSC code format"""
        if not self.ifsc_code or len(self.ifsc_code) != 11:
            raise ValueError("IFSC code must be exactly 11 characters")
        
        # IFSC format: First 4 letters (bank code), 5th character is 0, last 6 are alphanumeric
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', self.ifsc_code.upper()):
            raise ValueError("Invalid IFSC code format (e.g., SBIN0001234)")
    
    def _validate_account_holder_name(self) -> None:
        """Validate account holder name"""
        if not self.account_holder_name or not self.account_holder_name.strip():
            raise ValueError("Account holder name is required")
        
        if len(self.account_holder_name.strip()) < 2:
            raise ValueError("Account holder name must be at least 2 characters long")
        
        # Check for valid characters (letters, spaces, dots, hyphens)
        if not re.match(r'^[A-Za-z\s\.\-]+$', self.account_holder_name):
            raise ValueError("Account holder name can only contain letters, spaces, dots, and hyphens")
    
    def _validate_account_type(self) -> None:
        """Validate account type"""
        valid_types = ['savings', 'current', 'salary', 'fixed_deposit', 'recurring_deposit']
        if self.account_type.lower() not in valid_types:
            raise ValueError(f"Account type must be one of: {', '.join(valid_types)}")
    
    def get_formatted_account_number(self) -> str:
        """Get formatted account number for display"""
        clean_account = re.sub(r'\s+', '', self.account_number)
        # Show only last 4 digits for security
        if len(clean_account) > 4:
            return f"****{clean_account[-4:]}"
        return clean_account
    
    def get_masked_account_number(self) -> str:
        """Get masked account number for security"""
        clean_account = re.sub(r'\s+', '', self.account_number)
        if len(clean_account) <= 4:
            return "*" * len(clean_account)
        
        # Show first 2 and last 4 digits
        return f"{clean_account[:2]}{'*' * (len(clean_account) - 6)}{clean_account[-4:]}"
    
    def get_bank_code(self) -> str:
        """Extract bank code from IFSC"""
        return self.ifsc_code[:4] if self.ifsc_code else ""
    
    def get_branch_code(self) -> str:
        """Extract branch code from IFSC"""
        return self.ifsc_code[5:] if len(self.ifsc_code) >= 11 else ""
    
    def is_valid_for_payment(self) -> bool:
        """Check if bank details are complete for payment processing"""
        return bool(
            self.account_number and 
            self.bank_name and 
            self.ifsc_code and 
            self.account_holder_name
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "account_number": self.account_number,
            "bank_name": self.bank_name,
            "ifsc_code": self.ifsc_code,
            "account_holder_name": self.account_holder_name,
            "branch_name": self.branch_name,
            "branch_address": self.branch_address,
            "account_type": self.account_type,
            "formatted_account_number": self.get_formatted_account_number(),
            "masked_account_number": self.get_masked_account_number(),
            "bank_code": self.get_bank_code(),
            "branch_code": self.get_branch_code(),
            "is_valid_for_payment": self.is_valid_for_payment()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BankDetails':
        """Create from dictionary"""
        return cls(
            account_number=data["account_number"],
            bank_name=data["bank_name"],
            ifsc_code=data["ifsc_code"],
            account_holder_name=data["account_holder_name"],
            branch_name=data.get("branch_name"),
            branch_address=data.get("branch_address"),
            account_type=data.get("account_type")
        )
    
    def __str__(self) -> str:
        """String representation"""
        return f"BankDetails(bank={self.bank_name}, account={self.get_formatted_account_number()})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"BankDetails(bank_name='{self.bank_name}', ifsc='{self.ifsc_code}', account='{self.get_masked_account_number()}')" 