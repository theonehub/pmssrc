"""
Legacy Public Holiday Model - DEPRECATED
This model is being replaced by the new domain-driven architecture.
Please use the new domain entities and DTOs instead:
- domain.entities.public_holiday.PublicHoliday
- application.dto.public_holiday_dto.*
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PublicHoliday(BaseModel):
    """
    DEPRECATED: Legacy public holiday model.
    Use domain.entities.public_holiday.PublicHoliday instead.
    
    This model will be removed in a future version.
    Migration guide:
    1. Use PublicHolidayCreateRequestDTO for API requests
    2. Use PublicHolidayResponseDTO for API responses
    3. Use domain.entities.public_holiday.PublicHoliday for business logic
    """
    holiday_id: Optional[str] = None
    name: str
    date: datetime
    day: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = None
    is_active: bool = True 