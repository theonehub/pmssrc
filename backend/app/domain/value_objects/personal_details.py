"""
Personal Details Value Object
Encapsulates personal information for users following DDD principles
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date
import re

from app.domain.value_objects.user_credentials import Gender


@dataclass(frozen=True)
class PersonalDetails:
    """
    Value object for personal details.
    
    Follows SOLID principles:
    - SRP: Only handles personal information
    - OCP: Can be extended with new personal fields
    - LSP: Can be substituted anywhere PersonalDetails is expected
    - ISP: Focused interface for personal data
    - DIP: Doesn't depend on concrete implementations
    """
    
    gender: Gender
    date_of_birth: date
    mobile: str
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    uan_number: Optional[str] = None
    esi_number: Optional[str] = None
    
    def __post_init__(self):
        """Validate personal details after initialization"""
        self._validate_mobile()
        if self.pan_number:
            self._validate_pan_number()
        if self.aadhar_number:
            self._validate_aadhar_number()
        if self.uan_number:
            self._validate_uan_number()
        if self.esi_number:
            self._validate_esi_number()
    
    def _validate_mobile(self) -> None:
        """Validate mobile number format"""
        if not self.mobile:
            raise ValueError("Mobile number is required")
        
        # Remove any non-digit characters
        digits_only = re.sub(r'\D', '', self.mobile)
        
        # Check if it's a valid Indian mobile number
        if not re.match(r'^[6-9]\d{9}$', digits_only):
            raise ValueError("Invalid mobile number format. Must be a 10-digit Indian mobile number")
    
    def _validate_pan_number(self) -> None:
        """Validate PAN number format"""
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', self.pan_number):
            raise ValueError("Invalid PAN number format. Must be in format ABCDE1234F")
    
    def _validate_aadhar_number(self) -> None:
        """Validate Aadhar number format"""
        # Remove any non-digit characters
        digits_only = re.sub(r'\D', '', self.aadhar_number)
        
        if not re.match(r'^\d{12}$', digits_only):
            raise ValueError("Invalid Aadhar number format. Must be 12 digits")
    
    def _validate_uan_number(self) -> None:
        """Validate UAN number format"""
        # Remove any non-digit characters
        digits_only = re.sub(r'\D', '', self.uan_number)
        
        if not re.match(r'^\d{12}$', digits_only):
            raise ValueError("Invalid UAN number format. Must be 12 digits")
    
    def _validate_esi_number(self) -> None:
        """Validate ESI number format"""
        # ESI number format: 10 digits
        digits_only = re.sub(r'\D', '', self.esi_number)
        
        if not re.match(r'^\d{10}$', digits_only):
            raise ValueError("Invalid ESI number format. Must be 10 digits")
    
    def get_age(self) -> int:
        """Calculate age from date of birth"""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def get_formatted_mobile(self) -> str:
        """Get formatted mobile number"""
        digits_only = re.sub(r'\D', '', self.mobile)
        return f"+91 {digits_only[:5]} {digits_only[5:]}"
    
    def get_masked_pan(self) -> Optional[str]:
        """Get masked PAN number for display"""
        if not self.pan_number:
            return None
        return f"{self.pan_number[:3]}XX{self.pan_number[5:9]}X"
    
    def get_masked_aadhar(self) -> Optional[str]:
        """Get masked Aadhar number for display"""
        if not self.aadhar_number:
            return None
        digits_only = re.sub(r'\D', '', self.aadhar_number)
        return f"XXXX XXXX {digits_only[-4:]}"
    
    def is_adult(self) -> bool:
        """Check if person is adult (18+ years)"""
        return self.get_age() >= 18
    
    def is_senior_citizen(self) -> bool:
        """Check if person is senior citizen (60+ years)"""
        return self.get_age() >= 60
    
    def has_complete_documents(self) -> bool:
        """Check if all required documents are provided"""
        return bool(self.pan_number and self.aadhar_number)
    
    def get_document_completion_percentage(self) -> float:
        """Get document completion percentage"""
        total_docs = 4  # PAN, Aadhar, UAN, ESI
        completed_docs = 0
        
        if self.pan_number:
            completed_docs += 1
        if self.aadhar_number:
            completed_docs += 1
        if self.uan_number:
            completed_docs += 1
        if self.esi_number:
            completed_docs += 1
        
        return (completed_docs / total_docs) * 100
    
    def get_missing_documents(self) -> list:
        """Get list of missing documents"""
        missing = []
        
        if not self.pan_number:
            missing.append("PAN Card")
        if not self.aadhar_number:
            missing.append("Aadhar Card")
        if not self.uan_number:
            missing.append("UAN Number")
        if not self.esi_number:
            missing.append("ESI Number")
        
        return missing
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "gender": self.gender.value,
            "date_of_birth": self.date_of_birth.isoformat(),
            "mobile": self.mobile,
            "pan_number": self.pan_number,
            "aadhar_number": self.aadhar_number,
            "uan_number": self.uan_number,
            "esi_number": self.esi_number,
            "age": self.get_age(),
            "formatted_mobile": self.get_formatted_mobile(),
            "masked_pan": self.get_masked_pan(),
            "masked_aadhar": self.get_masked_aadhar(),
            "is_adult": self.is_adult(),
            "is_senior_citizen": self.is_senior_citizen(),
            "document_completion_percentage": self.get_document_completion_percentage(),
            "missing_documents": self.get_missing_documents()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PersonalDetails':
        """Create from dictionary"""
        return cls(
            gender=Gender(data["gender"]),
            date_of_birth=date.fromisoformat(data["date_of_birth"]),
            mobile=data["mobile"],
            pan_number=data.get("pan_number"),
            aadhar_number=data.get("aadhar_number"),
            uan_number=data.get("uan_number"),
            esi_number=data.get("esi_number")
        )
    
    def __str__(self) -> str:
        """String representation"""
        return f"PersonalDetails(gender={self.gender.value}, age={self.get_age()}, mobile={self.get_formatted_mobile()})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"PersonalDetails(gender={self.gender}, date_of_birth={self.date_of_birth}, mobile='{self.mobile}')" 