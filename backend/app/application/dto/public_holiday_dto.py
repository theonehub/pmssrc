"""
Public Holiday Data Transfer Objects
DTOs for public holiday API requests and responses
"""

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
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PublicHolidayBusinessRuleError(Exception):
    """Exception raised for public holiday business rule violations"""
    def __init__(self, message: str):
        self.message = message
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


class PublicHolidaySearchFiltersDTO(BaseModel):
    """DTO for public holiday search filters"""
    year: Optional[int] = Field(None, description="Filter by year")
    month: Optional[int] = Field(None, ge=1, le=12, description="Filter by month")
    category: Optional[HolidayCategory] = Field(None, description="Filter by category")
    observance: Optional[HolidayObservance] = Field(None, description="Filter by observance")
    active_only: bool = Field(True, description="Return only active holidays")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records")


class PublicHolidayImportResultDTO(BaseModel):
    """DTO for public holiday import results"""
    total_processed: int = Field(..., description="Total holidays processed")
    successful_imports: int = Field(..., description="Number of successful imports")
    failed_imports: int = Field(..., description="Number of failed imports")
    errors: List[str] = Field(default_factory=list, description="Import errors")
    warnings: List[str] = Field(default_factory=list, description="Import warnings")


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