"""
Public Holiday Data Transfer Objects
DTOs for public holiday API requests and responses
"""

import typing
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field, validator


# Simple enums for public holidays
class HolidayCategory(str, Enum):
    NATIONAL = "national"
    RELIGIOUS = "religious"
    CULTURAL = "cultural"
    REGIONAL = "regional"
    OPTIONAL = "optional"


class HolidayObservance(str, Enum):
    MANDATORY = "mandatory"
    OPTIONAL = "optional"
    REGIONAL = "regional"


class HolidayRecurrence(str, Enum):
    ANNUAL = "annual"
    ONE_TIME = "one_time"
    IRREGULAR = "irregular"


# Exception classes
class PublicHolidayValidationError(Exception):
    """Exception raised for public holiday validation errors"""
    def __init__(self, message: str, details: Any = None):
        self.message = message
        self.details = details
        if details is not None:
            super().__init__(message, details)
        else:
            super().__init__(message)


class PublicHolidayDTOValidationError(Exception):
    """Exception raised for public holiday DTO validation errors"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PublicHolidayBusinessRuleError(Exception):
    """Exception raised for public holiday business rule violations"""
    def __init__(self, message: str, details: Any = None):
        self.message = message
        self.details = details
        if details is not None:
            super().__init__(message, details)
        else:
            super().__init__(message)


class PublicHolidayNotFoundError(Exception):
    """Exception raised when public holiday is not found"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


# DTO Classes
class PublicHolidayCreateRequestDTO(BaseModel):
    """DTO for creating public holidays"""
    name: str = Field(..., description="Holiday name")
    holiday_date: date = Field(..., description="Holiday date")
    description: Optional[str] = Field(None, description="Holiday description")
    category: HolidayCategory = Field(HolidayCategory.NATIONAL, description="Holiday category")
    observance: HolidayObservance = Field(HolidayObservance.MANDATORY, description="Holiday observance")
    recurrence: HolidayRecurrence = Field(HolidayRecurrence.ANNUAL, description="Holiday recurrence")
    is_active: bool = Field(True, description="Whether holiday is active")
    location_specific: Optional[str] = Field(None, description="Location specific holiday information")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Holiday name is required")
        if len(v) > 100:
            raise ValueError("Holiday name cannot exceed 100 characters")
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 500:
            raise ValueError("Description cannot exceed 500 characters")
        return v


class PublicHolidayUpdateRequestDTO(BaseModel):
    """DTO for updating public holidays"""
    name: Optional[str] = Field(None, description="Holiday name")
    holiday_date: Optional[date] = Field(None, description="Holiday date")
    description: Optional[str] = Field(None, description="Holiday description")
    category: Optional[HolidayCategory] = Field(None, description="Holiday category")
    observance: Optional[HolidayObservance] = Field(None, description="Holiday observance")
    recurrence: Optional[HolidayRecurrence] = Field(None, description="Holiday recurrence")
    is_active: Optional[bool] = Field(None, description="Whether holiday is active")
    location_specific: Optional[str] = Field(None, description="Location specific holiday information")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Holiday name cannot be empty")
            if len(v) > 100:
                raise ValueError("Holiday name cannot exceed 100 characters")
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError("Description cannot exceed 500 characters")
        return v


class PublicHolidayResponseDTO(BaseModel):
    """DTO for public holiday responses"""
    id: str = Field(..., description="Holiday ID")
    name: str = Field(..., description="Holiday name")
    holiday_date: date = Field(..., description="Holiday date")
    description: Optional[str] = Field(None, description="Holiday description")
    category: HolidayCategory = Field(..., description="Holiday category")
    observance: HolidayObservance = Field(..., description="Holiday observance")
    recurrence: HolidayRecurrence = Field(..., description="Holiday recurrence")
    is_active: bool = Field(..., description="Whether holiday is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="Created by user")
    updated_by: Optional[str] = Field(None, description="Updated by user")

    @classmethod
    def from_domain(cls, holiday) -> 'PublicHolidayResponseDTO':
        """Create DTO from domain entity"""
        return cls(
            id=str(holiday.id),
            name=holiday.name,
            holiday_date=holiday.date,
            description=holiday.description,
            category=HolidayCategory.NATIONAL,  # Default value for now
            observance=HolidayObservance.MANDATORY,  # Default value for now
            recurrence=HolidayRecurrence.ANNUAL,  # Default value for now
            is_active=holiday.is_active,
            created_at=holiday.created_at,
            updated_at=holiday.updated_at,
            created_by=holiday.created_by,
            updated_by=holiday.updated_by
        )
    
    @classmethod
    def from_entity(cls, holiday) -> 'PublicHolidayResponseDTO':
        """Create DTO from domain entity (alias for from_domain)"""
        return cls.from_domain(holiday)


class PublicHolidaySearchFiltersDTO(BaseModel):
    """DTO for public holiday search filters"""
    year: Optional[int] = Field(None, description="Filter by year")
    month: Optional[int] = Field(None, ge=1, le=12, description="Filter by month")
    category: Optional[HolidayCategory] = Field(None, description="Filter by category")
    observance: Optional[HolidayObservance] = Field(None, description="Filter by observance")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    sort_by: str = Field("holiday_date", description="Sort field")
    sort_order: str = Field("asc", description="Sort order (asc/desc)")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(100, ge=1, le=1000, description="Number of records per page")


class PublicHolidayImportResultDTO(BaseModel):
    """DTO for public holiday import results"""
    total_processed: int = Field(..., description="Total holidays processed")
    successful_imports: List[Dict[str, Any]] = Field(default_factory=list, description="Successfully imported holiday data")
    failed_imports: int = Field(..., description="Number of failed imports")
    errors: List[str] = Field(default_factory=list, description="Import errors")
    warnings: List[str] = Field(default_factory=list, description="Import warnings")


class PublicHolidaySummaryDTO(BaseModel):
    """DTO for public holiday summary (lightweight version)"""
    id: str = Field(..., description="Holiday ID")
    name: str = Field(..., description="Holiday name")
    holiday_date: date = Field(..., description="Holiday date")
    category: HolidayCategory = Field(..., description="Holiday category")
    observance: HolidayObservance = Field(..., description="Holiday observance")
    is_active: bool = Field(..., description="Whether holiday is active")
    
    @classmethod
    def from_domain(cls, holiday) -> 'PublicHolidaySummaryDTO':
        """Create DTO from domain entity"""
        return cls(
            id=str(holiday.id),
            name=holiday.name,
            holiday_date=holiday.date,
            category=HolidayCategory.NATIONAL,  # Default value for now
            observance=HolidayObservance.MANDATORY,  # Default value for now
            is_active=holiday.is_active
        )


class HolidayCalendarDTO(BaseModel):
    """DTO for holiday calendar data"""
    year: int = Field(..., description="Calendar year")
    month: Optional[int] = Field(None, description="Calendar month (if monthly view)")
    holidays: List[Dict[str, Any]] = Field(default_factory=list, description="Holiday data")
    total_holidays: int = Field(0, description="Total number of holidays")
    mandatory_holidays: int = Field(0, description="Number of mandatory holidays")
    optional_holidays: int = Field(0, description="Number of optional holidays")


class PublicHolidayListResponseDTO(BaseModel):
    """DTO for paginated public holiday list responses"""
    holidays: List[PublicHolidayResponseDTO] = Field(default_factory=list, description="Holiday items")
    total_count: int = Field(0, description="Total number of holidays")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(100, description="Number of items per page")
    total_pages: int = Field(0, description="Total number of pages")
    has_next: bool = Field(False, description="Whether there is a next page")
    has_previous: bool = Field(False, description="Whether there is a previous page")


class ImportPublicHolidayRequestDTO(BaseModel):
    """DTO for importing multiple public holidays"""
    file_content: bytes = Field(..., description="File content as bytes")
    file_name: str = Field(..., description="Original file name")
    file_type: str = Field(..., description="File type (xlsx, xls, csv)")
    holidays: Optional[List[Dict[str, Any]]] = Field(None, description="Parsed holiday data")
    overwrite_existing: bool = Field(False, description="Whether to overwrite existing holidays")
    validate_only: bool = Field(False, description="Whether to only validate without importing")
    source: Optional[str] = Field(None, description="Import source identifier")


# Aliases for backward compatibility with service interface expectations
CreatePublicHolidayRequestDTO = PublicHolidayCreateRequestDTO
UpdatePublicHolidayRequestDTO = PublicHolidayUpdateRequestDTO


# Utility functions for DTO validation
def validate_holiday_dto_data(data: Dict[str, Any]) -> List[str]:
    """Validate holiday DTO data and return list of errors"""
    errors = []
    
    try:
        PublicHolidayCreateRequestDTO.from_dict(data)
    except PublicHolidayValidationError as e:
        errors.append(e.message)
    
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