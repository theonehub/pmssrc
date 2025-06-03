"""
Update Public Holiday Use Case
Business logic for updating public holidays
"""

import logging
from datetime import datetime, date
from typing import Optional

from app.application.dto.public_holiday_dto import (
    PublicHolidayUpdateRequestDTO,
    PublicHolidayResponseDTO,
    PublicHolidayNotFoundError,
    PublicHolidayValidationError
)
from app.application.interfaces.repositories.public_holiday_repository import (
    PublicHolidayCommandRepository,
    PublicHolidayQueryRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.notification_service import NotificationService
from app.domain.entities.public_holiday import PublicHoliday


logger = logging.getLogger(__name__)


class UpdatePublicHolidayUseCaseError(Exception):
    """Exception raised for update public holiday use case errors"""
    pass


class UpdatePublicHolidayUseCase:
    """
    Use case for updating public holidays.
    
    Follows SOLID principles:
    - SRP: Only handles public holiday updates
    - OCP: Extensible through composition and events
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for update operations
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
    
    async def execute(self, holiday_id: str, request_dto: PublicHolidayUpdateRequestDTO, updated_by: str) -> PublicHolidayResponseDTO:
        """
        Execute the update public holiday use case.
        
        Steps:
        1. Validate request data
        2. Get existing holiday
        3. Check business rules
        4. Update domain objects
        5. Save to repository
        6. Publish domain events
        7. Send notifications
        8. Return response
        """
        
        logger.info(f"Updating public holiday: {holiday_id}")
        
        try:
            # Step 1: Validate request data
            self._validate_request(request_dto)
            
            # Step 2: Get existing holiday
            existing_holiday = await self.query_repository.get_by_id(holiday_id)
            if not existing_holiday:
                raise PublicHolidayNotFoundError(f"Holiday not found: {holiday_id}")
            
            # Step 3: Check business rules
            await self._validate_business_rules(existing_holiday, request_dto)
            
            # Step 4: Update domain objects
            updated_holiday = self._update_domain_objects(existing_holiday, request_dto, updated_by)
            
            # Step 5: Save to repository
            success = await self.command_repository.update(updated_holiday)
            if not success:
                raise UpdatePublicHolidayUseCaseError("Failed to update public holiday")
            
            # Step 6: Publish domain events
            self._publish_domain_events(updated_holiday)
            
            # Step 7: Send notifications (optional, non-blocking)
            self._send_notifications(updated_holiday)
            
            # Step 8: Return response
            response_dto = PublicHolidayResponseDTO.from_domain(updated_holiday)
            
            logger.info(f"Successfully updated public holiday: {holiday_id}")
            return response_dto
            
        except PublicHolidayNotFoundError:
            raise
        except PublicHolidayValidationError as e:
            logger.error(f"Validation error updating public holiday: {e}")
            raise UpdatePublicHolidayUseCaseError(f"Validation failed: {e.message}")
        except Exception as e:
            logger.error(f"Error updating public holiday: {e}")
            raise UpdatePublicHolidayUseCaseError(f"Failed to update public holiday: {str(e)}")
    
    def _validate_request(self, request_dto: PublicHolidayUpdateRequestDTO):
        """Validate the request DTO"""
        # Basic validation
        if request_dto.name is not None and not request_dto.name.strip():
            raise PublicHolidayValidationError("Holiday name cannot be empty")
    
    async def _validate_business_rules(self, existing_holiday: PublicHoliday, request_dto: PublicHolidayUpdateRequestDTO):
        """Validate business rules"""
        
        # Business Rule 1: Cannot update past holidays to active if they are currently inactive
        if request_dto.is_active and not existing_holiday.is_active:
            if existing_holiday.date_range.is_past():
                raise UpdatePublicHolidayUseCaseError("Cannot activate holidays for past dates")
        
        # Business Rule 2: Check for name conflicts if name is being updated
        if request_dto.name and request_dto.name != existing_holiday.holiday_type.name:
            year = existing_holiday.date_range.start_date.year
            existing_holidays = await self.query_repository.get_by_year(year, include_inactive=False)
            for holiday in existing_holidays:
                if (holiday.holiday_id != existing_holiday.holiday_id and 
                    holiday.holiday_type.name.lower() == request_dto.name.lower()):
                    raise UpdatePublicHolidayUseCaseError(
                        f"Holiday with name '{request_dto.name}' already exists in {year}"
                    )
        
        # Business Rule 3: Check for date conflicts if date is being updated
        if request_dto.holiday_date:
            new_date = request_dto.holiday_date
            if new_date != existing_holiday.date_range.start_date:
                conflicting_holiday = await self.query_repository.get_by_date(new_date)
                if (conflicting_holiday and 
                    conflicting_holiday.holiday_id != existing_holiday.holiday_id and 
                    conflicting_holiday.is_active):
                    raise UpdatePublicHolidayUseCaseError(
                        f"Active holiday '{conflicting_holiday.holiday_type.name}' already exists on {new_date}"
                    )
    
    def _update_domain_objects(self, existing_holiday: PublicHoliday, request_dto: PublicHolidayUpdateRequestDTO, updated_by: str) -> PublicHoliday:
        """Update domain objects from DTO"""
        
        # Update holiday details if provided
        if request_dto.name or request_dto.description:
            existing_holiday.update_holiday_details(
                name=request_dto.name,
                description=request_dto.description,
                updated_by=updated_by
            )
        
        # Update date if provided
        if request_dto.holiday_date:
            existing_holiday.change_date(
                new_date=request_dto.holiday_date,
                updated_by=updated_by,
                reason="Holiday date updated via API"
            )
        
        # Update active status if provided
        if request_dto.is_active is not None:
            if request_dto.is_active and not existing_holiday.is_active:
                existing_holiday.activate(updated_by=updated_by)
            elif not request_dto.is_active and existing_holiday.is_active:
                existing_holiday.deactivate(updated_by=updated_by, reason="Holiday deactivated via API")
        
        return existing_holiday
    
    def _publish_domain_events(self, holiday: PublicHoliday):
        """Publish domain events"""
        try:
            events = holiday.get_domain_events()
            for event in events:
                self.event_publisher.publish(event)
            
            # Clear events after publishing
            holiday.clear_domain_events()
            
            logger.debug(f"Published {len(events)} domain events for holiday: {holiday.holiday_id}")
            
        except Exception as e:
            # Non-critical error - log but don't fail the operation
            logger.warning(f"Failed to publish domain events: {e}")
    
    def _send_notifications(self, holiday: PublicHoliday):
        """Send notifications (optional, non-blocking)"""
        try:
            if self.notification_service:
                # Send notification to administrators about holiday update
                self.notification_service.send_holiday_updated_notification(holiday)
                logger.debug(f"Sent update notification for holiday: {holiday.holiday_id}")
        except Exception as e:
            # Non-critical error - log but don't fail the operation
            logger.warning(f"Failed to send notifications: {e}") 