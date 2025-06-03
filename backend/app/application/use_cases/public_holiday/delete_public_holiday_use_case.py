"""
Delete Public Holiday Use Case
Business logic for deleting (deactivating) public holidays
"""

import logging
from typing import Optional

from app.application.dto.public_holiday_dto import (
    PublicHolidayNotFoundError,
    PublicHolidayBusinessRuleError
)
from app.application.interfaces.repositories.public_holiday_repository import (
    PublicHolidayCommandRepository,
    PublicHolidayQueryRepository
)
from app.application.interfaces.services.event_publisher import EventPublisher
from app.application.interfaces.services.notification_service import NotificationService
from app.domain.entities.public_holiday import PublicHoliday


logger = logging.getLogger(__name__)


class DeletePublicHolidayUseCaseError(Exception):
    """Exception raised for delete public holiday use case errors"""
    pass


class DeletePublicHolidayUseCase:
    """
    Use case for deleting (deactivating) public holidays.
    
    Follows SOLID principles:
    - SRP: Only handles public holiday deletion
    - OCP: Extensible through composition and events
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused interface for deletion operations
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
    
    async def execute(self, holiday_id: str, deleted_by: str) -> None:
        """
        Execute the delete public holiday use case.
        
        Steps:
        1. Get existing holiday
        2. Check business rules
        3. Deactivate domain object
        4. Save to repository
        5. Publish domain events
        6. Send notifications
        """
        
        logger.info(f"Deleting public holiday: {holiday_id}")
        
        try:
            # Step 1: Get existing holiday
            existing_holiday = await self.query_repository.get_by_id(holiday_id)
            if not existing_holiday:
                raise PublicHolidayNotFoundError(f"Holiday not found: {holiday_id}")
            
            # Step 2: Check business rules
            self._validate_business_rules(existing_holiday)
            
            # Step 3: Deactivate domain object
            existing_holiday.deactivate(
                updated_by=deleted_by,
                reason="Holiday deleted via API"
            )
            
            # Step 4: Save to repository (soft delete by deactivation)
            success = await self.command_repository.update(existing_holiday)
            if not success:
                raise DeletePublicHolidayUseCaseError("Failed to delete public holiday")
            
            # Step 5: Publish domain events
            self._publish_domain_events(existing_holiday)
            
            # Step 6: Send notifications (optional, non-blocking)
            self._send_notifications(existing_holiday)
            
            logger.info(f"Successfully deleted public holiday: {holiday_id}")
            
        except PublicHolidayNotFoundError:
            raise
        except PublicHolidayBusinessRuleError as e:
            logger.error(f"Business rule error deleting public holiday: {e}")
            raise DeletePublicHolidayUseCaseError(f"Business rule violation: {e.message}")
        except Exception as e:
            logger.error(f"Error deleting public holiday: {e}")
            raise DeletePublicHolidayUseCaseError(f"Failed to delete public holiday: {str(e)}")
    
    def _validate_business_rules(self, holiday: PublicHoliday):
        """Validate business rules for deletion"""
        
        # Business Rule 1: Already inactive holidays cannot be deleted again
        if not holiday.is_active:
            raise PublicHolidayBusinessRuleError("Holiday is already inactive")
        
        # Business Rule 2: Optional - Could add rules about not deleting holidays 
        # that are referenced by other systems, employee leave records, etc.
        # For now, we allow soft deletion of any active holiday
        
        logger.debug(f"Business rule validation passed for holiday: {holiday.holiday_id}")
    
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
                # Send notification to administrators about holiday deletion
                self.notification_service.send_holiday_deleted_notification(holiday)
                logger.debug(f"Sent deletion notification for holiday: {holiday.holiday_id}")
        except Exception as e:
            # Non-critical error - log but don't fail the operation
            logger.warning(f"Failed to send notifications: {e}") 