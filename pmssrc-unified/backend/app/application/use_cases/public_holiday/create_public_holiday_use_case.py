"""
Create Public Holiday Use Case
Business logic for creating public holidays
"""

import logging
from datetime import datetime, date
from typing import Optional
import uuid

from app.application.dto.public_holiday_dto import (
    PublicHolidayCreateRequestDTO,
    PublicHolidayResponseDTO,
    PublicHolidayDTOValidationError
)
from app.application.interfaces.repositories.public_holiday_repository import (
    PublicHolidayCommandRepository,
    PublicHolidayQueryRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.notification_service import NotificationService
from app.domain.entities.public_holiday import PublicHoliday

logger = logging.getLogger(__name__)


class CreatePublicHolidayUseCaseError(Exception):
    """Exception raised for create public holiday use case errors"""
    pass


class CreatePublicHolidayUseCase:
    """
    Use case for creating public holidays.
    
    Follows SOLID principles:
    - SRP: Only handles public holiday creation
    - OCP: Extensible through composition and events
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for creation operations
    - DIP: Depends on abstractions (repositories, services)
    """
    
    def __init__(
        self,
        command_repository: PublicHolidayCommandRepository,
        query_repository: PublicHolidayQueryRepository,
        event_publisher: EventPublisher,
        notification_service: Optional[NotificationService] = None
    ):
        self.command_repository = command_repository
        self.query_repository = query_repository
        self.event_publisher = event_publisher
        self.notification_service = notification_service
    
    async def execute(self, request_dto: PublicHolidayCreateRequestDTO, employee_id: str) -> PublicHolidayResponseDTO:
        """
        Execute the create public holiday use case.
        
        Steps:
        1. Validate request data
        2. Check business rules
        3. Create domain objects
        4. Save to repository
        5. Publish domain events
        6. Send notifications
        7. Return response
        """
        
        logger.info(f"Creating public holiday: {request_dto.name} by employee: {employee_id}")
        
        try:
            # Step 1: Validate request data
            self._validate_request(request_dto)
            
            # Step 2: Check business rules
            await self._validate_business_rules(request_dto)
            
            # Step 3: Create domain objects
            holiday = self._create_domain_objects(request_dto, employee_id)
            
            # Step 4: Save to repository
            success = await self.command_repository.save(holiday)
            if not success:
                raise CreatePublicHolidayUseCaseError("Failed to save public holiday")
            
            # Step 5: Return response
            response_dto = PublicHolidayResponseDTO.from_domain(holiday)
            
            logger.info(f"Successfully created public holiday: {holiday.holiday_id}")
            return response_dto
            
        except PublicHolidayDTOValidationError as e:
            logger.error(f"Validation error creating public holiday: {e}")
            raise CreatePublicHolidayUseCaseError(f"Validation failed: {', '.join(e.errors)}")
        
        except Exception as e:
            logger.error(f"Error creating public holiday: {e}")
            raise CreatePublicHolidayUseCaseError(f"Failed to create public holiday: {str(e)}")
    
    def _validate_request(self, request_dto: PublicHolidayCreateRequestDTO):
        """Validate the request DTO"""
        # DTO validation is handled in __post_init__
        # Additional business validation can be added here
        pass
    
    async def _validate_business_rules(self, request_dto: PublicHolidayCreateRequestDTO):
        """Validate business rules"""
        
        # Parse dates - DTO uses date objects directly
        holiday_date = request_dto.holiday_date
        
        # Business Rule 1: Cannot create holidays for past dates (unless explicitly allowed)
        if holiday_date < date.today():
            logger.warning(f"Attempting to create holiday for past date: {holiday_date}")
            # Allow past dates for historical data import
        
        # Business Rule 2: Check for conflicts with existing holidays
        existing_holiday = await self.query_repository.get_by_date(holiday_date)
        if existing_holiday and existing_holiday.is_active:
            raise CreatePublicHolidayUseCaseError(
                f"Active holiday '{existing_holiday.holiday_name}' already exists on {holiday_date}"
            )
        
        # Business Rule 3: Validate name uniqueness for the same year
        year = holiday_date.year
        existing_holidays = await self.query_repository.get_by_year(year, include_inactive=False)
        for existing in existing_holidays:
            if existing.holiday_name.lower() == request_dto.name.lower():
                raise CreatePublicHolidayUseCaseError(
                    f"Holiday with name '{request_dto.name}' already exists in {year}"
                )
        
    def _create_domain_objects(self, request_dto: PublicHolidayCreateRequestDTO, employee_id: str) -> PublicHoliday:
        """Create domain objects from DTO"""
        
        # Parse dates - DTO uses date objects directly, not ISO strings
        holiday_date = request_dto.holiday_date
        holiday = PublicHoliday(
            holiday_id=str(uuid.uuid4()),
            holiday_name=request_dto.name,
            holiday_date=holiday_date,
            is_active=request_dto.is_active,
            created_by=employee_id,
            updated_by=employee_id,
            description=request_dto.description,
            location_specific=request_dto.location_specific
        )
        return holiday
    