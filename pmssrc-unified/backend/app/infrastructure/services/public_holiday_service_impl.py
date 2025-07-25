"""
Public Holiday Service Implementation
SOLID-compliant implementation of public holiday service interface
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.application.interfaces.services.public_holiday_service import PublicHolidayService
from app.application.interfaces.repositories.public_holiday_repository import PublicHolidayRepository
from app.application.dto.public_holiday_dto import (
    CreatePublicHolidayRequestDTO,
    UpdatePublicHolidayRequestDTO,
    PublicHolidayResponseDTO,
    PublicHolidayListResponseDTO,
    PublicHolidaySearchFiltersDTO,
    ImportPublicHolidayRequestDTO,
    PublicHolidayValidationError,
    PublicHolidayBusinessRuleError,
    PublicHolidayNotFoundError
)
from app.domain.entities.public_holiday import PublicHoliday
from app.domain.value_objects.public_holiday_id import PublicHolidayId
from app.infrastructure.services.notification_service import NotificationService
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)


class PublicHolidayServiceImpl(PublicHolidayService):
    """
    Complete implementation of public holiday service interface.
    
    Follows SOLID principles:
    - SRP: Delegates to specific use cases and repositories
    - OCP: Extensible through dependency injection
    - LSP: Implements all interface contracts correctly
    - ISP: Implements focused interfaces
    - DIP: Depends on abstractions, not concretions
    """
    
    def __init__(
        self,
        public_holiday_repository: PublicHolidayRepository,
        notification_service: Optional[NotificationService] = None
    ):
        """Initialize service with dependencies."""
        self.public_holiday_repository = public_holiday_repository
        self.notification_service = notification_service
        self.logger = logging.getLogger(__name__)
    
    # Command Operations
    async def create_public_holiday(
        self, 
        request: CreatePublicHolidayRequestDTO, 
        current_user: CurrentUser
    ) -> PublicHolidayResponseDTO:
        """Create a new public holiday."""
        try:
            logger.info(f"Creating public holiday in organisation: {current_user.hostname}")
            
            # Validate request
            validation_errors = self._validate_create_request(request)
            if validation_errors:
                raise PublicHolidayValidationError("Validation failed", validation_errors)
            
            # Create domain entity
            public_holiday = PublicHoliday.create(
                id=PublicHolidayId.generate(),
                name=request.name,
                date=request.holiday_date,
                description=request.description,
                is_active=request.is_active,
                created_by=current_user.employee_id
            )
            
            # Apply business rules
            business_rule_errors = await self._validate_business_rules(public_holiday, current_user)
            if business_rule_errors:
                raise PublicHolidayBusinessRuleError("Business rule violation", business_rule_errors)
            
            # Save entity
            saved_holiday = await self.public_holiday_repository.save(public_holiday, current_user.hostname)
            
            # Send notification
            if self.notification_service:
                await self.notification_service.notify_holiday_created(saved_holiday)
            
            return PublicHolidayResponseDTO.from_entity(saved_holiday)
            
        except Exception as e:
            logger.error(f"Error creating public holiday in organisation {current_user.hostname}: {e}")
            raise
    
    async def update_public_holiday(
        self,
        holiday_id: str,
        request: UpdatePublicHolidayRequestDTO,
        current_user: CurrentUser
    ) -> PublicHolidayResponseDTO:
        """Update an existing public holiday."""
        try:
            logger.info(f"Updating public holiday {holiday_id} in organisation: {current_user.hostname}")
            
            # Get existing holiday
            existing_holiday = await self.public_holiday_repository.get_by_id(
                PublicHolidayId(holiday_id), 
                current_user.hostname
            )
            if not existing_holiday:
                raise PublicHolidayNotFoundError(f"Public holiday not found: {holiday_id}")
            
            # Validate request
            validation_errors = self._validate_update_request(request)
            if validation_errors:
                raise PublicHolidayValidationError("Validation failed", validation_errors)
            
            # Update entity
            updated_holiday = existing_holiday.update(
                name=request.name if request.name is not None else existing_holiday.name,
                date=request.holiday_date if request.holiday_date is not None else existing_holiday.date,
                description=request.description if request.description is not None else existing_holiday.description,
                is_active=request.is_active if request.is_active is not None else existing_holiday.is_active,
                updated_by=current_user.employee_id
            )
            
            # Apply business rules
            business_rule_errors = await self._validate_business_rules(updated_holiday, current_user)
            if business_rule_errors:
                raise PublicHolidayBusinessRuleError("Business rule violation", business_rule_errors)
            
            # Save updated entity
            saved_holiday = await self.public_holiday_repository.save(updated_holiday, current_user.hostname)
            
            # Send notification
            if self.notification_service:
                await self.notification_service.notify_holiday_updated(saved_holiday)
            
            return PublicHolidayResponseDTO.from_entity(saved_holiday)
            
        except Exception as e:
            logger.error(f"Error updating public holiday {holiday_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def delete_public_holiday(
        self,
        holiday_id: str,
        force: bool,
        current_user: CurrentUser
    ) -> bool:
        """Delete a public holiday."""
        try:
            logger.info(f"Deleting public holiday {holiday_id} in organisation: {current_user.hostname}")
            
            # Get existing holiday
            existing_holiday = await self.public_holiday_repository.get_by_id(
                PublicHolidayId(holiday_id), 
                current_user.hostname
            )
            if not existing_holiday:
                raise PublicHolidayNotFoundError(f"Public holiday not found: {holiday_id}")
            
            # Check business rules for deletion
            if not force:
                business_rule_errors = await self._validate_deletion_rules(existing_holiday, current_user)
                if business_rule_errors:
                    raise PublicHolidayBusinessRuleError("Cannot delete holiday", business_rule_errors)
            
            # Delete entity
            result = await self.public_holiday_repository.delete(
                PublicHolidayId(holiday_id), 
                current_user.hostname
            )
            
            # Send notification
            if result and self.notification_service:
                await self.notification_service.notify_holiday_deleted(holiday_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error deleting public holiday {holiday_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def import_public_holidays(
        self, 
        request: ImportPublicHolidayRequestDTO,
        current_user: CurrentUser
    ) -> List[PublicHolidayResponseDTO]:
        """Import multiple public holidays."""
        try:
            logger.info(f"Importing public holidays in organisation: {current_user.hostname}")
            
            # Create import use case
            from app.application.use_cases.public_holiday.import_public_holidays_use_case import ImportPublicHolidaysUseCase
            
            # Create a simple event publisher
            class SimpleEventPublisher:
                async def publish_event(self, event_type: str, data: dict):
                    logger.info(f"Event published: {event_type} - {data}")
            
            event_publisher = SimpleEventPublisher()
            
            import_use_case = ImportPublicHolidaysUseCase(
                command_repository=self.public_holiday_repository,
                query_repository=self.public_holiday_repository,
                event_publisher=event_publisher,
                notification_service=self.notification_service
            )
            
            # Execute import
            result = await import_use_case.execute(
                file_data=request.file_content,
                filename=request.file_name,
                imported_by=current_user.employee_id,
                hostname=current_user.hostname
            )
            
            # If there are validation errors, raise them
            if result.errors:
                error_messages = "\n".join(result.errors)
                raise PublicHolidayValidationError(f"Import validation failed:\n{error_messages}")
            
            # Return successfully imported holidays
            imported_holidays = []
            for holiday_data in result.successful_imports:
                # Get the saved holiday from repository
                holidays = await self.public_holiday_repository.find_by_name_and_date(
                    holiday_data['name'], 
                    holiday_data['date'], 
                    current_user.hostname
                )
                if holidays:
                    imported_holidays.append(PublicHolidayResponseDTO.from_entity(holidays[0]))
            
            logger.info(f"Successfully imported {len(imported_holidays)} holidays")
            return imported_holidays
            
        except Exception as e:
            logger.error(f"Error importing public holidays in organisation {current_user.hostname}: {e}")
            raise
    
    # Query Operations
    async def get_public_holiday_by_id(
        self, 
        holiday_id: str, 
        current_user: CurrentUser
    ) -> Optional[PublicHolidayResponseDTO]:
        """Get public holiday by ID."""
        try:
            holiday = await self.public_holiday_repository.get_by_id(
                PublicHolidayId(holiday_id), 
                current_user.hostname
            )
            if not holiday:
                return None
            return PublicHolidayResponseDTO.from_entity(holiday)
        except Exception as e:
            logger.error(f"Error getting public holiday {holiday_id} in organisation {current_user.hostname}: {e}")
            raise
    
    async def list_public_holidays(
        self, 
        filters: PublicHolidaySearchFiltersDTO, 
        current_user: CurrentUser
    ) -> PublicHolidayListResponseDTO:
        """List public holidays with optional filters."""
        try:
            holidays, total_count = await self.public_holiday_repository.find_with_filters(
                filters, current_user.hostname
            )
            
            holiday_responses = [
                PublicHolidayResponseDTO.from_entity(holiday) for holiday in holidays
            ]
            
            total_pages = (total_count + filters.page_size - 1) // filters.page_size if filters.page_size > 0 else 1
            
            return PublicHolidayListResponseDTO(
                holidays=holiday_responses,
                total_count=total_count,
                page=filters.page,
                page_size=filters.page_size,
                total_pages=total_pages,
                has_next=filters.page < total_pages,
                has_previous=filters.page > 1
            )
        except Exception as e:
            logger.error(f"Error listing public holidays in organisation {current_user.hostname}: {e}")
            raise
    
    async def get_holidays_by_date_range(
        self, 
        start_date: date, 
        end_date: date,
        current_user: CurrentUser
    ) -> List[PublicHolidayResponseDTO]:
        """Get holidays within a date range."""
        try:
            holidays = await self.public_holiday_repository.find_by_date_range(
                start_date, end_date, current_user.hostname
            )
            return [PublicHolidayResponseDTO.from_entity(holiday) for holiday in holidays]
        except Exception as e:
            logger.error(f"Error getting holidays by date range in organisation {current_user.hostname}: {e}")
            raise
    
    # Validation Operations
    async def validate_holiday_request(
        self, 
        request: CreatePublicHolidayRequestDTO,
        current_user: CurrentUser
    ) -> List[str]:
        """Validate public holiday creation request."""
        try:
            errors = self._validate_create_request(request)
            
            # Add business rule validation
            if not errors:
                # Create temporary entity for business rule validation
                temp_holiday = PublicHoliday.create(
                    id=PublicHolidayId.generate(),
                    name=request.name,
                    date=request.holiday_date,
                    description=request.description,
                    is_active=request.is_active,
                    created_by=current_user.employee_id
                )
                
                business_errors = await self._validate_business_rules(temp_holiday, current_user)
                errors.extend(business_errors)
            
            return errors
        except Exception as e:
            logger.error(f"Error validating public holiday request: {e}")
            raise
    
    # Notification Operations
    async def notify_holiday_created(self, holiday: PublicHolidayResponseDTO) -> bool:
        """Notify about public holiday creation."""
        try:
            if self.notification_service:
                return await self.notification_service.send_notification(
                    message=f"New public holiday created: {holiday.name}",
                    recipients=["admin"],
                    notification_type="holiday_created"
                )
            return False
        except Exception as e:
            logger.error(f"Error sending holiday created notification: {e}")
            return False
    
    async def notify_holiday_updated(self, holiday: PublicHolidayResponseDTO) -> bool:
        """Notify about public holiday update."""
        try:
            if self.notification_service:
                return await self.notification_service.send_notification(
                    message=f"Public holiday updated: {holiday.name}",
                    recipients=["admin"],
                    notification_type="holiday_updated"
                )
            return False
        except Exception as e:
            logger.error(f"Error sending holiday updated notification: {e}")
            return False
    
    async def notify_holiday_deleted(self, holiday_id: str) -> bool:
        """Notify about public holiday deletion."""
        try:
            if self.notification_service:
                return await self.notification_service.send_notification(
                    message=f"Public holiday deleted: {holiday_id}",
                    recipients=["admin"],
                    notification_type="holiday_deleted"
                )
            return False
        except Exception as e:
            logger.error(f"Error sending holiday deleted notification: {e}")
            return False
    
    # Private helper methods
    def _validate_create_request(self, request: CreatePublicHolidayRequestDTO) -> List[str]:
        """Validate create request data."""
        errors = []
        
        if not request.name or not request.name.strip():
            errors.append("Holiday name is required")
        
        if not request.holiday_date:
            errors.append("Holiday date is required")
        
        if request.holiday_date and request.holiday_date < date.today():
            errors.append("Holiday date cannot be in the past")
        
        return errors
    
    def _validate_update_request(self, request: UpdatePublicHolidayRequestDTO) -> List[str]:
        """Validate update request data."""
        errors = []
        
        if request.name is not None and (not request.name or not request.name.strip()):
            errors.append("Holiday name cannot be empty")
        
        if request.holiday_date and request.holiday_date < date.today():
            errors.append("Holiday date cannot be in the past")
        
        return errors
    
    async def _validate_business_rules(
        self, 
        holiday: PublicHoliday, 
        current_user: CurrentUser
    ) -> List[str]:
        """Validate business rules for holiday."""
        errors = []
        
        # Check for duplicate holidays on the same date
        existing_holidays = await self.public_holiday_repository.find_by_date(
            holiday.date, current_user.hostname
        )
        
        for existing in existing_holidays:
            if existing.id != holiday.id and existing.is_active:
                errors.append(f"A holiday already exists on {holiday.date}")
                break
        
        return errors
    
    async def _validate_deletion_rules(
        self, 
        holiday: PublicHoliday, 
        current_user: CurrentUser
    ) -> List[str]:
        """Validate business rules for holiday deletion."""
        errors = []
        
        # Check if holiday is in the past
        if holiday.date < date.today():
            errors.append("Cannot delete past holidays")
        
        # Add more business rules as needed
        
        return errors 