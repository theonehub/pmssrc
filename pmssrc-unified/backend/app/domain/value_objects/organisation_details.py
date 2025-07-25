"""
Organisation Details Value Objects
Handles organisation contact information, address, and tax details
"""

import re
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class OrganisationType(Enum):
    """Organisation type enumeration"""
    PRIVATE_LIMITED = "private_limited"
    PUBLIC_LIMITED = "public_limited"
    PARTNERSHIP = "partnership"
    SOLE_PROPRIETORSHIP = "sole_proprietorship"
    LLP = "llp"  # Limited Liability Partnership
    GOVERNMENT = "government"
    NGO = "ngo"
    TRUST = "trust"
    SOCIETY = "society"


class OrganisationStatus(Enum):
    """Organisation status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


@dataclass(frozen=True)
class ContactInformation:
    """
    Value object for organisation contact information.
    
    Follows SOLID principles:
    - SRP: Encapsulates contact information logic
    - OCP: Extensible through new contact methods
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for contact operations
    - DIP: Depends on abstractions (string)
    """
    
    email: str
    phone: str
    website: Optional[str] = None
    fax: Optional[str] = None
    
    def __post_init__(self):
        """Validate contact information"""
        self._validate_email()
        self._validate_phone()
        if self.website:
            self._validate_website()
        if self.fax:
            self._validate_fax()
    
    def _validate_email(self):
        """Validate email format"""
        if not self.email or not self.email.strip():
            raise ValueError("Email is required")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email.strip()):
            raise ValueError("Invalid email format")
    
    def _validate_phone(self):
        """Validate phone number"""
        if not self.phone or not self.phone.strip():
            raise ValueError("Phone number is required")
        
        # Remove all non-digit characters for validation
        digits_only = re.sub(r'\D', '', self.phone)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError("Phone number must be between 10 and 15 digits")
    
    def _validate_website(self):
        """Validate website URL"""
        if not self.website.strip():
            return
        
        url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        if not re.match(url_pattern, self.website.strip()):
            raise ValueError("Invalid website URL format")
    
    def _validate_fax(self):
        """Validate fax number"""
        if not self.fax.strip():
            return
        
        digits_only = re.sub(r'\D', '', self.fax)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError("Fax number must be between 10 and 15 digits")
    
    def get_formatted_phone(self) -> str:
        """Get formatted phone number"""
        digits_only = re.sub(r'\D', '', self.phone)
        if len(digits_only) == 10:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        return self.phone
    
    def get_domain_from_email(self) -> str:
        """Extract domain from email"""
        return self.email.split('@')[1] if '@' in self.email else ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "email": self.email,
            "phone": self.phone,
            "website": self.website,
            "fax": self.fax
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ContactInformation':
        """Create from dictionary representation"""
        return cls(
            email=data["email"],
            phone=data["phone"],
            website=data.get("website"),
            fax=data.get("fax")
        )


@dataclass(frozen=True)
class Address:
    """
    Value object for organisation address.
    
    Follows SOLID principles:
    - SRP: Encapsulates address logic
    - OCP: Extensible through new address components
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for address operations
    - DIP: Depends on abstractions (string)
    """
    
    street_address: str
    city: str
    state: str
    country: str
    pin_code: str
    landmark: Optional[str] = None
    
    def __post_init__(self):
        """Validate address components"""
        if not self.street_address or not self.street_address.strip():
            raise ValueError("Street address is required")
        
        if not self.city or not self.city.strip():
            raise ValueError("City is required")
        
        if not self.state or not self.state.strip():
            raise ValueError("State is required")
        
        if not self.country or not self.country.strip():
            raise ValueError("Country is required")
        
        if not self.pin_code or not self.pin_code.strip():
            raise ValueError("Pin code is required")
        
        # Validate pin code format (basic validation)
        pin_digits = re.sub(r'\D', '', self.pin_code)
        if len(pin_digits) < 4 or len(pin_digits) > 10:
            raise ValueError("Pin code must be between 4 and 10 digits")
    
    def get_full_address(self) -> str:
        """Get formatted full address"""
        parts = [self.street_address, self.city, self.state, self.country, self.pin_code]
        if self.landmark:
            parts.insert(1, f"Near {self.landmark}")
        return ", ".join(part.strip() for part in parts if part and part.strip())
    
    def get_short_address(self) -> str:
        """Get short address (city, state, country)"""
        return f"{self.city}, {self.state}, {self.country}"
    
    def is_indian_address(self) -> bool:
        """Check if address is in India"""
        return self.country.lower() in ["india", "in", "ind"]
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "street_address": self.street_address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "pin_code": self.pin_code,
            "landmark": self.landmark
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Address':
        """Create from dictionary representation"""
        return cls(
            street_address=data["street_address"],
            city=data["city"],
            state=data["state"],
            country=data["country"],
            pin_code=data["pin_code"],
            landmark=data.get("landmark")
        )


@dataclass(frozen=True)
class TaxInformation:
    """
    Value object for organisation tax information.
    
    Follows SOLID principles:
    - SRP: Encapsulates tax information logic
    - OCP: Extensible through new tax types
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for tax operations
    - DIP: Depends on abstractions (string)
    """
    
    pan_number: str
    gst_number: Optional[str] = None
    tan_number: Optional[str] = None
    cin_number: Optional[str] = None  # Corporate Identification Number
    esi_establishment_id: Optional[str] = None  # ESI Establishment ID
    pf_establishment_id: Optional[str] = None  # PF Establishment ID
    
    def __post_init__(self):
        """Validate tax information"""
        self._validate_pan_number()
        if self.gst_number:
            self._validate_gst_number()
        if self.tan_number:
            self._validate_tan_number()
        if self.cin_number:
            self._validate_cin_number()
    
    def _validate_pan_number(self):
        """Validate PAN number format"""
        if not self.pan_number or not self.pan_number.strip():
            raise ValueError("PAN number is required")
        
        # PAN format: AAAAA9999A (5 letters, 4 digits, 1 letter)
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pan_pattern, self.pan_number.upper()):
            raise ValueError("Invalid PAN number format. Expected format: AAAAA9999A")
    
    def _validate_gst_number(self):
        """Validate GST number format"""
        if not self.gst_number.strip():
            return
        
        # GST format: 99AAAAA9999A9Z9 (15 characters)
        gst_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
        if not re.match(gst_pattern, self.gst_number.upper()):
            raise ValueError("Invalid GST number format")
    
    def _validate_tan_number(self):
        """Validate TAN number format"""
        if not self.tan_number.strip():
            return
        
        # TAN format: AAAA99999A (4 letters, 5 digits, 1 letter)
        tan_pattern = r'^[A-Z]{4}[0-9]{5}[A-Z]{1}$'
        if not re.match(tan_pattern, self.tan_number.upper()):
            raise ValueError("Invalid TAN number format. Expected format: AAAA99999A")
    
    def _validate_cin_number(self):
        """Validate CIN number format"""
        if not self.cin_number.strip():
            return
        
        # CIN format: L99999AA9999AAA999999 (21 characters)
        cin_pattern = r'^[A-Z]{1}[0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$'
        if not re.match(cin_pattern, self.cin_number.upper()):
            raise ValueError("Invalid CIN number format")
    
    def is_gst_registered(self) -> bool:
        """Check if organisation is GST registered"""
        return bool(self.gst_number and self.gst_number.strip())
    
    def get_state_code_from_gst(self) -> Optional[str]:
        """Extract state code from GST number"""
        if self.is_gst_registered():
            return self.gst_number[:2]
        return None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "pan_number": self.pan_number,
            "gst_number": self.gst_number,
            "tan_number": self.tan_number,
            "cin_number": self.cin_number,
            "esi_establishment_id": self.esi_establishment_id,
            "pf_establishment_id": self.pf_establishment_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TaxInformation':
        """Create from dictionary representation"""
        return cls(
            pan_number=data["pan_number"],
            gst_number=data.get("gst_number"),
            tan_number=data.get("tan_number"),
            cin_number=data.get("cin_number"),
            esi_establishment_id=data.get("esi_establishment_id"),
            pf_establishment_id=data.get("pf_establishment_id")
        ) 
    
@dataclass(frozen=True)
class BankDetails:
    """Value object for organisation bank details."""
    bank_name: str
    account_number: str
    ifsc_code: str
    branch_name: str
    branch_address: str
    account_type: str
    account_holder_name: str