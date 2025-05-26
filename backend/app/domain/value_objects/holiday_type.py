"""
Holiday Type Value Object
Immutable representation of public holiday types and categories
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass


class HolidayCategory(Enum):
    """Enumeration of holiday categories"""
    NATIONAL = "national"
    RELIGIOUS = "religious"
    CULTURAL = "cultural"
    REGIONAL = "regional"
    COMPANY = "company"
    SEASONAL = "seasonal"
    INTERNATIONAL = "international"


class HolidayObservance(Enum):
    """Enumeration of holiday observance types"""
    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    FLOATING = "floating"
    SUBSTITUTE = "substitute"


class HolidayRecurrence(Enum):
    """Enumeration of holiday recurrence patterns"""
    ANNUAL = "annual"
    LUNAR = "lunar"
    ONE_TIME = "one_time"
    MOVEABLE = "moveable"


@dataclass(frozen=True)
class HolidayType:
    """
    Value object representing a holiday type.
    
    Follows SOLID principles:
    - SRP: Only represents holiday type data
    - OCP: Extensible through composition
    - LSP: Maintains value object contracts
    - ISP: Focused interface for holiday types
    - DIP: No dependencies on external systems
    """
    
    code: str
    name: str
    category: HolidayCategory
    observance: HolidayObservance
    recurrence: HolidayRecurrence
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate holiday type data"""
        if not self.code or len(self.code.strip()) == 0:
            raise ValueError("Holiday type code cannot be empty")
        
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Holiday type name cannot be empty")
        
        if len(self.code) > 10:
            raise ValueError("Holiday type code cannot exceed 10 characters")
        
        if len(self.name) > 100:
            raise ValueError("Holiday type name cannot exceed 100 characters")
        
        # Ensure code is uppercase
        object.__setattr__(self, 'code', self.code.upper().strip())
        object.__setattr__(self, 'name', self.name.strip())
    
    @classmethod
    def national_holiday(
        cls,
        code: str,
        name: str,
        description: Optional[str] = None
    ) -> 'HolidayType':
        """Factory method for national holidays"""
        return cls(
            code=code,
            name=name,
            category=HolidayCategory.NATIONAL,
            observance=HolidayObservance.MANDATORY,
            recurrence=HolidayRecurrence.ANNUAL,
            description=description
        )
    
    @classmethod
    def religious_holiday(
        cls,
        code: str,
        name: str,
        description: Optional[str] = None,
        is_lunar: bool = False
    ) -> 'HolidayType':
        """Factory method for religious holidays"""
        return cls(
            code=code,
            name=name,
            category=HolidayCategory.RELIGIOUS,
            observance=HolidayObservance.OPTIONAL,
            recurrence=HolidayRecurrence.LUNAR if is_lunar else HolidayRecurrence.ANNUAL,
            description=description
        )
    
    @classmethod
    def company_holiday(
        cls,
        code: str,
        name: str,
        description: Optional[str] = None
    ) -> 'HolidayType':
        """Factory method for company-specific holidays"""
        return cls(
            code=code,
            name=name,
            category=HolidayCategory.COMPANY,
            observance=HolidayObservance.MANDATORY,
            recurrence=HolidayRecurrence.ANNUAL,
            description=description
        )
    
    @classmethod
    def regional_holiday(
        cls,
        code: str,
        name: str,
        description: Optional[str] = None
    ) -> 'HolidayType':
        """Factory method for regional holidays"""
        return cls(
            code=code,
            name=name,
            category=HolidayCategory.REGIONAL,
            observance=HolidayObservance.OPTIONAL,
            recurrence=HolidayRecurrence.ANNUAL,
            description=description
        )
    
    @classmethod
    def floating_holiday(
        cls,
        code: str,
        name: str,
        description: Optional[str] = None
    ) -> 'HolidayType':
        """Factory method for floating holidays"""
        return cls(
            code=code,
            name=name,
            category=HolidayCategory.COMPANY,
            observance=HolidayObservance.FLOATING,
            recurrence=HolidayRecurrence.ANNUAL,
            description=description
        )
    
    def is_mandatory(self) -> bool:
        """Check if holiday is mandatory"""
        return self.observance == HolidayObservance.MANDATORY
    
    def is_optional(self) -> bool:
        """Check if holiday is optional"""
        return self.observance == HolidayObservance.OPTIONAL
    
    def is_floating(self) -> bool:
        """Check if holiday is floating"""
        return self.observance == HolidayObservance.FLOATING
    
    def is_recurring(self) -> bool:
        """Check if holiday is recurring"""
        return self.recurrence != HolidayRecurrence.ONE_TIME
    
    def is_lunar_based(self) -> bool:
        """Check if holiday follows lunar calendar"""
        return self.recurrence == HolidayRecurrence.LUNAR
    
    def is_moveable(self) -> bool:
        """Check if holiday date can move"""
        return self.recurrence == HolidayRecurrence.MOVEABLE
    
    def get_display_name(self) -> str:
        """Get formatted display name"""
        return f"{self.name} ({self.code})"
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "code": self.code,
            "name": self.name,
            "category": self.category.value,
            "observance": self.observance.value,
            "recurrence": self.recurrence.value,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HolidayType':
        """Create from dictionary"""
        return cls(
            code=data["code"],
            name=data["name"],
            category=HolidayCategory(data["category"]),
            observance=HolidayObservance(data["observance"]),
            recurrence=HolidayRecurrence(data["recurrence"]),
            description=data.get("description")
        )


# Common holiday types for easy reference
class CommonHolidayTypes:
    """Common holiday type definitions"""
    
    NEW_YEAR = HolidayType.national_holiday(
        "NY", "New Year's Day", "First day of the calendar year"
    )
    
    INDEPENDENCE_DAY = HolidayType.national_holiday(
        "ID", "Independence Day", "National independence celebration"
    )
    
    CHRISTMAS = HolidayType.religious_holiday(
        "XMAS", "Christmas Day", "Christian celebration of Jesus Christ's birth"
    )
    
    DIWALI = HolidayType.religious_holiday(
        "DIWALI", "Diwali", "Hindu festival of lights", is_lunar=True
    )
    
    EID = HolidayType.religious_holiday(
        "EID", "Eid al-Fitr", "Islamic celebration marking end of Ramadan", is_lunar=True
    )
    
    COMPANY_FOUNDATION = HolidayType.company_holiday(
        "FOUND", "Company Foundation Day", "Anniversary of company establishment"
    )
    
    FLOATING_PERSONAL = HolidayType.floating_holiday(
        "FLOAT", "Floating Personal Day", "Employee choice personal holiday"
    ) 