"""
Public Holiday Data Transfer Objects
DTOs for public holiday API requests and responses
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from domain.value_objects.holiday_type import HolidayCategory, HolidayObservance, HolidayRecurrence
from domain.value_objects.holiday_date_range import DateRangeType


class PublicHolidayDTOValidationError(Exception):
    """Exception raised for DTO validation errors"""
    
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Validation failed: {', '.join(errors)}")


@dataclass
class PublicHolidayCreateRequestDTO:
    """
    DTO for creating public holidays.
    
    Follows SOLID principles:
    - SRP: Only handles create request data
    - OCP: Extensible through composition
    - LSP: Maintains DTO contracts
    - ISP: Focused interface for creation
    - DIP: No dependencies on external systems
    """
    
    name: str
    holiday_date: str  # ISO format date string
    holiday_category: str
    holiday_observance: str = "mandatory"
    holiday_recurrence: str = "annual"
    description: Optional[str] = None
    notes: Optional[str] = None
    location_specific: Optional[str] = None
    substitute_for: Optional[str] = None
    end_date: Optional[str] = None  # For multi-day holidays
    is_half_day: bool = False
    half_day_period: Optional[str] = None
    created_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate DTO data"""
        errors = []
        
        # Validate required fields
        if not self.name or not self.name.strip():
            errors.append("Holiday name is required")
        
        if not self.holiday_date:
            errors.append("Holiday date is required")
        
        # Validate date format
        try:
            datetime.fromisoformat(self.holiday_date)
        except ValueError:
            errors.append("Holiday date must be in ISO format (YYYY-MM-DD)")
        
        # Validate end date if provided
        if self.end_date:
            try:
                end_date_obj = datetime.fromisoformat(self.end_date).date()
                start_date_obj = datetime.fromisoformat(self.holiday_date).date()
                if end_date_obj < start_date_obj:
                    errors.append("End date cannot be before start date")
            except ValueError:
                errors.append("End date must be in ISO format (YYYY-MM-DD)")
        
        # Validate category
        try:
            HolidayCategory(self.holiday_category)
        except ValueError:
            valid_categories = [cat.value for cat in HolidayCategory]
            errors.append(f"Invalid holiday category. Must be one of: {valid_categories}")
        
        # Validate observance
        try:
            HolidayObservance(self.holiday_observance)
        except ValueError:
            valid_observances = [obs.value for obs in HolidayObservance]
            errors.append(f"Invalid holiday observance. Must be one of: {valid_observances}")
        
        # Validate recurrence
        try:
            HolidayRecurrence(self.holiday_recurrence)
        except ValueError:
            valid_recurrences = [rec.value for rec in HolidayRecurrence]
            errors.append(f"Invalid holiday recurrence. Must be one of: {valid_recurrences}")
        
        # Validate half day settings
        if self.is_half_day:
            if self.half_day_period not in ["morning", "afternoon"]:
                errors.append("Half day period must be 'morning' or 'afternoon'")
            if self.end_date:
                errors.append("Half day holidays cannot span multiple days")
        
        # Validate name length
        if self.name and len(self.name) > 100:
            errors.append("Holiday name cannot exceed 100 characters")
        
        # Validate description length
        if self.description and len(self.description) > 500:
            errors.append("Description cannot exceed 500 characters")
        
        if errors:
            raise PublicHolidayDTOValidationError(errors)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PublicHolidayCreateRequestDTO':
        """Create DTO from dictionary"""
        return cls(
            name=data.get("name", ""),
            holiday_date=data.get("holiday_date", ""),
            holiday_category=data.get("holiday_category", ""),
            holiday_observance=data.get("holiday_observance", "mandatory"),
            holiday_recurrence=data.get("holiday_recurrence", "annual"),
            description=data.get("description"),
            notes=data.get("notes"),
            location_specific=data.get("location_specific"),
            substitute_for=data.get("substitute_for"),
            end_date=data.get("end_date"),
            is_half_day=data.get("is_half_day", False),
            half_day_period=data.get("half_day_period"),
            created_by=data.get("created_by")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "holiday_date": self.holiday_date,
            "holiday_category": self.holiday_category,
            "holiday_observance": self.holiday_observance,
            "holiday_recurrence": self.holiday_recurrence,
            "description": self.description,
            "notes": self.notes,
            "location_specific": self.location_specific,
            "substitute_for": self.substitute_for,
            "end_date": self.end_date,
            "is_half_day": self.is_half_day,
            "half_day_period": self.half_day_period,
            "created_by": self.created_by
        }


@dataclass
class PublicHolidayUpdateRequestDTO:
    """DTO for updating public holidays"""
    
    name: Optional[str] = None
    holiday_date: Optional[str] = None
    holiday_category: Optional[str] = None
    holiday_observance: Optional[str] = None
    holiday_recurrence: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    location_specific: Optional[str] = None
    substitute_for: Optional[str] = None
    end_date: Optional[str] = None
    is_half_day: Optional[bool] = None
    half_day_period: Optional[str] = None
    is_active: Optional[bool] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate DTO data"""
        errors = []
        
        # Validate name if provided
        if self.name is not None:
            if not self.name.strip():
                errors.append("Holiday name cannot be empty")
            elif len(self.name) > 100:
                errors.append("Holiday name cannot exceed 100 characters")
        
        # Validate date format if provided
        if self.holiday_date:
            try:
                datetime.fromisoformat(self.holiday_date)
            except ValueError:
                errors.append("Holiday date must be in ISO format (YYYY-MM-DD)")
        
        # Validate end date if provided
        if self.end_date:
            try:
                datetime.fromisoformat(self.end_date)
            except ValueError:
                errors.append("End date must be in ISO format (YYYY-MM-DD)")
        
        # Validate category if provided
        if self.holiday_category:
            try:
                HolidayCategory(self.holiday_category)
            except ValueError:
                valid_categories = [cat.value for cat in HolidayCategory]
                errors.append(f"Invalid holiday category. Must be one of: {valid_categories}")
        
        # Validate observance if provided
        if self.holiday_observance:
            try:
                HolidayObservance(self.holiday_observance)
            except ValueError:
                valid_observances = [obs.value for obs in HolidayObservance]
                errors.append(f"Invalid holiday observance. Must be one of: {valid_observances}")
        
        # Validate recurrence if provided
        if self.holiday_recurrence:
            try:
                HolidayRecurrence(self.holiday_recurrence)
            except ValueError:
                valid_recurrences = [rec.value for rec in HolidayRecurrence]
                errors.append(f"Invalid holiday recurrence. Must be one of: {valid_recurrences}")
        
        # Validate half day settings if provided
        if self.is_half_day is not None and self.is_half_day:
            if self.half_day_period and self.half_day_period not in ["morning", "afternoon"]:
                errors.append("Half day period must be 'morning' or 'afternoon'")
        
        # Validate description length if provided
        if self.description is not None and len(self.description) > 500:
            errors.append("Description cannot exceed 500 characters")
        
        if errors:
            raise PublicHolidayDTOValidationError(errors)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PublicHolidayUpdateRequestDTO':
        """Create DTO from dictionary"""
        return cls(
            name=data.get("name"),
            holiday_date=data.get("holiday_date"),
            holiday_category=data.get("holiday_category"),
            holiday_observance=data.get("holiday_observance"),
            holiday_recurrence=data.get("holiday_recurrence"),
            description=data.get("description"),
            notes=data.get("notes"),
            location_specific=data.get("location_specific"),
            substitute_for=data.get("substitute_for"),
            end_date=data.get("end_date"),
            is_half_day=data.get("is_half_day"),
            half_day_period=data.get("half_day_period"),
            is_active=data.get("is_active"),
            updated_by=data.get("updated_by")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "holiday_date": self.holiday_date,
            "holiday_category": self.holiday_category,
            "holiday_observance": self.holiday_observance,
            "holiday_recurrence": self.holiday_recurrence,
            "description": self.description,
            "notes": self.notes,
            "location_specific": self.location_specific,
            "substitute_for": self.substitute_for,
            "end_date": self.end_date,
            "is_half_day": self.is_half_day,
            "half_day_period": self.half_day_period,
            "is_active": self.is_active,
            "updated_by": self.updated_by
        }


@dataclass
class PublicHolidayResponseDTO:
    """DTO for public holiday responses"""
    
    holiday_id: str
    name: str
    holiday_type: Dict[str, Any]
    date_range: Dict[str, Any]
    is_active: bool
    created_at: str
    updated_at: str
    created_by: Optional[str]
    updated_by: Optional[str]
    notes: Optional[str]
    location_specific: Optional[str]
    substitute_for: Optional[str]
    
    @classmethod
    def from_domain(cls, holiday) -> 'PublicHolidayResponseDTO':
        """Create DTO from domain entity"""
        return cls(
            holiday_id=holiday.holiday_id,
            name=holiday.holiday_type.name,
            holiday_type=holiday.holiday_type.to_dict(),
            date_range=holiday.date_range.to_dict(),
            is_active=holiday.is_active,
            created_at=holiday.created_at.isoformat(),
            updated_at=holiday.updated_at.isoformat(),
            created_by=holiday.created_by,
            updated_by=holiday.updated_by,
            notes=holiday.notes,
            location_specific=holiday.location_specific,
            substitute_for=holiday.substitute_for
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "holiday_id": self.holiday_id,
            "name": self.name,
            "holiday_type": self.holiday_type,
            "date_range": self.date_range,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "notes": self.notes,
            "location_specific": self.location_specific,
            "substitute_for": self.substitute_for
        }


@dataclass
class PublicHolidaySummaryDTO:
    """DTO for public holiday summaries"""
    
    holiday_id: str
    name: str
    category: str
    observance: str
    date: str
    formatted_date: str
    is_active: bool
    is_upcoming: bool
    days_until: int
    
    @classmethod
    def from_domain(cls, holiday) -> 'PublicHolidaySummaryDTO':
        """Create DTO from domain entity"""
        return cls(
            holiday_id=holiday.holiday_id,
            name=holiday.holiday_type.name,
            category=holiday.holiday_type.category.value,
            observance=holiday.holiday_type.observance.value,
            date=holiday.date_range.start_date.isoformat(),
            formatted_date=holiday.date_range.get_formatted_date_range(),
            is_active=holiday.is_active,
            is_upcoming=holiday.date_range.is_upcoming(),
            days_until=holiday.date_range.days_until_holiday()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "holiday_id": self.holiday_id,
            "name": self.name,
            "category": self.category,
            "observance": self.observance,
            "date": self.date,
            "formatted_date": self.formatted_date,
            "is_active": self.is_active,
            "is_upcoming": self.is_upcoming,
            "days_until": self.days_until
        }


@dataclass
class HolidayCalendarDTO:
    """DTO for holiday calendar responses"""
    
    year: int
    month: Optional[int]
    holidays: List[Dict[str, Any]]
    total_holidays: int
    mandatory_holidays: int
    optional_holidays: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "year": self.year,
            "month": self.month,
            "holidays": self.holidays,
            "total_holidays": self.total_holidays,
            "mandatory_holidays": self.mandatory_holidays,
            "optional_holidays": self.optional_holidays
        }


@dataclass
class HolidayImportRequestDTO:
    """DTO for bulk holiday import requests"""
    
    holidays: List[Dict[str, Any]]
    import_mode: str = "create_only"  # "create_only", "update_existing", "replace_all"
    validate_conflicts: bool = True
    imported_by: Optional[str] = None
    
    def __post_init__(self):
        """Validate import request"""
        errors = []
        
        if not self.holidays:
            errors.append("At least one holiday must be provided")
        
        if self.import_mode not in ["create_only", "update_existing", "replace_all"]:
            errors.append("Import mode must be 'create_only', 'update_existing', or 'replace_all'")
        
        # Validate each holiday
        for i, holiday_data in enumerate(self.holidays):
            try:
                PublicHolidayCreateRequestDTO.from_dict(holiday_data)
            except PublicHolidayDTOValidationError as e:
                errors.extend([f"Holiday {i+1}: {error}" for error in e.errors])
        
        if errors:
            raise PublicHolidayDTOValidationError(errors)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HolidayImportRequestDTO':
        """Create DTO from dictionary"""
        return cls(
            holidays=data.get("holidays", []),
            import_mode=data.get("import_mode", "create_only"),
            validate_conflicts=data.get("validate_conflicts", True),
            imported_by=data.get("imported_by")
        )


@dataclass
class HolidayImportResponseDTO:
    """DTO for bulk holiday import responses"""
    
    import_batch_id: str
    total_holidays: int
    successful_imports: int
    failed_imports: int
    conflicts_detected: int
    import_summary: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "import_batch_id": self.import_batch_id,
            "total_holidays": self.total_holidays,
            "successful_imports": self.successful_imports,
            "failed_imports": self.failed_imports,
            "conflicts_detected": self.conflicts_detected,
            "import_summary": self.import_summary
        }


# Utility functions for DTO validation
def validate_holiday_dto_data(data: Dict[str, Any]) -> List[str]:
    """Validate holiday DTO data and return list of errors"""
    errors = []
    
    try:
        PublicHolidayCreateRequestDTO.from_dict(data)
    except PublicHolidayDTOValidationError as e:
        errors.extend(e.errors)
    
    return errors


def get_holiday_category_options() -> List[Dict[str, str]]:
    """Get holiday category options for UI"""
    return [
        {"value": cat.value, "label": cat.value.replace("_", " ").title()}
        for cat in HolidayCategory
    ]


def get_holiday_observance_options() -> List[Dict[str, str]]:
    """Get holiday observance options for UI"""
    return [
        {"value": obs.value, "label": obs.value.replace("_", " ").title()}
        for obs in HolidayObservance
    ]


def get_holiday_recurrence_options() -> List[Dict[str, str]]:
    """Get holiday recurrence options for UI"""
    return [
        {"value": rec.value, "label": rec.value.replace("_", " ").title()}
        for rec in HolidayRecurrence
    ] 