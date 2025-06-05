"""
Public Holiday Service Interface
Following Interface Segregation Principle for public holiday business operations
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.application.dto.public_holiday_dto import (
    CreatePublicHolidayRequestDTO,
    UpdatePublicHolidayRequestDTO,
    PublicHolidayResponseDTO,
    PublicHolidayListResponseDTO,
    PublicHolidaySearchFiltersDTO,
    ImportPublicHolidayRequestDTO
)


class PublicHolidayCommandService(ABC):
    """
    Service interface for public holiday command operations.
    """
    
    @abstractmethod
    async def create_public_holiday(self, request: CreatePublicHolidayRequestDTO) -> PublicHolidayResponseDTO:
        """Create a new public holiday."""
        pass
    
    @abstractmethod
    async def update_public_holiday(self, holiday_id: str, request: UpdatePublicHolidayRequestDTO) -> PublicHolidayResponseDTO:
        """Update an existing public holiday."""
        pass
    
    @abstractmethod
    async def delete_public_holiday(self, holiday_id: str) -> bool:
        """Delete a public holiday."""
        pass
    
    @abstractmethod
    async def import_public_holidays(self, request: ImportPublicHolidayRequestDTO) -> List[PublicHolidayResponseDTO]:
        """Import multiple public holidays."""
        pass


class PublicHolidayQueryService(ABC):
    """
    Service interface for public holiday query operations.
    """
    
    @abstractmethod
    async def get_public_holiday_by_id(self, holiday_id: str) -> Optional[PublicHolidayResponseDTO]:
        """Get public holiday by ID."""
        pass
    
    @abstractmethod
    async def list_public_holidays(self, filters: Optional[PublicHolidaySearchFiltersDTO] = None) -> PublicHolidayListResponseDTO:
        """List public holidays with optional filters."""
        pass
    
    @abstractmethod
    async def get_holidays_by_date_range(self, start_date: date, end_date: date) -> List[PublicHolidayResponseDTO]:
        """Get holidays within a date range."""
        pass


class PublicHolidayValidationService(ABC):
    """
    Service interface for public holiday validation operations.
    """
    
    @abstractmethod
    async def validate_holiday_request(self, request: CreatePublicHolidayRequestDTO) -> List[str]:
        """Validate public holiday creation request."""
        pass


class PublicHolidayNotificationService(ABC):
    """
    Service interface for public holiday notification operations.
    """
    
    @abstractmethod
    async def notify_holiday_created(self, holiday: PublicHolidayResponseDTO) -> bool:
        """Notify about public holiday creation."""
        pass
    
    @abstractmethod
    async def notify_holiday_updated(self, holiday: PublicHolidayResponseDTO) -> bool:
        """Notify about public holiday update."""
        pass
    
    @abstractmethod
    async def notify_holiday_deleted(self, holiday_id: str) -> bool:
        """Notify about public holiday deletion."""
        pass


class PublicHolidayService(
    PublicHolidayCommandService,
    PublicHolidayQueryService,
    PublicHolidayValidationService,
    PublicHolidayNotificationService
):
    """
    Combined public holiday service interface.
    """
    pass 