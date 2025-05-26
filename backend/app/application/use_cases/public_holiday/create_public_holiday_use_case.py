"""
Create Public Holiday Use Case
Business logic for creating public holidays
"""

import logging
from datetime import datetime, date
from typing import Optional

from application.dto.public_holiday_dto import (
    PublicHolidayCreateRequestDTO,
    PublicHolidayResponseDTO,
    PublicHolidayDTOValidationError
)
from application.interfaces.repositories.public_holiday_repository import (
    PublicHolidayCommandRepository,
    PublicHolidayQueryRepository
)
from application.interfaces.services.event_publisher import EventPublisher
from application.interfaces.services.notification_service import NotificationService
from domain.entities.public_holiday import PublicHoliday
from domain.value_objects.holiday_type import HolidayType, HolidayCategory, HolidayObservance, HolidayRecurrence
from domain.value_objects.holiday_date_range import HolidayDateRange


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
    
    def execute(self, request_dto: PublicHolidayCreateRequestDTO) -> PublicHolidayResponseDTO:
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
        
        logger.info(f"Creating public holiday: {request_dto.name}")
        
        try:
            # Step 1: Validate request data
            self._validate_request(request_dto)
            
            # Step 2: Check business rules
            self._validate_business_rules(request_dto)
            
            # Step 3: Create domain objects
            holiday = self._create_domain_objects(request_dto)
            
            # Step 4: Save to repository
            success = self.command_repository.save(holiday)
            if not success:
                raise CreatePublicHolidayUseCaseError("Failed to save public holiday")
            
            # Step 5: Publish domain events
            self._publish_domain_events(holiday)
            
            # Step 6: Send notifications (optional, non-blocking)
            self._send_notifications(holiday)
            
            # Step 7: Return response
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
    
    def _validate_business_rules(self, request_dto: PublicHolidayCreateRequestDTO):
        """Validate business rules"""
        
        # Parse dates
        holiday_date = datetime.fromisoformat(request_dto.holiday_date).date()
        end_date = None
        if request_dto.end_date:
            end_date = datetime.fromisoformat(request_dto.end_date).date()
        
        # Business Rule 1: Cannot create holidays for past dates (unless explicitly allowed)
        if holiday_date < date.today():
            logger.warning(f"Attempting to create holiday for past date: {holiday_date}")
            # Allow past dates for historical data import
            # raise CreatePublicHolidayUseCaseError("Cannot create holidays for past dates")
        
        # Business Rule 2: Check for conflicts with existing holidays
        existing_holiday = self.query_repository.get_by_date(holiday_date)
        if existing_holiday and existing_holiday.is_active:
            raise CreatePublicHolidayUseCaseError(
                f"Active holiday '{existing_holiday.holiday_type.name}' already exists on {holiday_date}"
            )
        
        # Business Rule 3: Validate multi-day holiday logic
        if end_date:
            if end_date <= holiday_date:
                raise CreatePublicHolidayUseCaseError("End date must be after start date")
            
            # Check for conflicts in the date range
            conflicting_holidays = self.query_repository.get_by_date_range(
                holiday_date, end_date, include_inactive=False
            )
            if conflicting_holidays:
                conflict_names = [h.holiday_type.name for h in conflicting_holidays]
                raise CreatePublicHolidayUseCaseError(
                    f"Conflicts with existing holidays: {', '.join(conflict_names)}"
                )
        
        # Business Rule 4: Validate half-day holiday constraints
        if request_dto.is_half_day:
            if request_dto.end_date:
                raise CreatePublicHolidayUseCaseError("Half-day holidays cannot span multiple days")
            if not request_dto.half_day_period:
                raise CreatePublicHolidayUseCaseError("Half-day period must be specified")
        
        # Business Rule 5: Validate name uniqueness for the same year
        year = holiday_date.year
        existing_holidays = self.query_repository.get_by_year(year, include_inactive=False)
        for existing in existing_holidays:
            if existing.holiday_type.name.lower() == request_dto.name.lower():
                raise CreatePublicHolidayUseCaseError(
                    f"Holiday with name '{request_dto.name}' already exists in {year}"
                )
        
        # Business Rule 6: Validate regional holiday constraints
        if request_dto.location_specific:
            category = HolidayCategory(request_dto.holiday_category)
            if category != HolidayCategory.REGIONAL:
                raise CreatePublicHolidayUseCaseError(
                    "Location-specific holidays must have 'regional' category"
                )
        
        # Business Rule 7: Validate substitute holiday constraints
        if request_dto.substitute_for:
            # Check if the original holiday exists
            original_holidays = self.query_repository.search_holidays(
                search_term=request_dto.substitute_for
            )
            if not original_holidays:
                raise CreatePublicHolidayUseCaseError(
                    f"Original holiday '{request_dto.substitute_for}' not found"
                )
    
    def _create_domain_objects(self, request_dto: PublicHolidayCreateRequestDTO) -> PublicHoliday:
        """Create domain objects from DTO"""
        
        # Parse dates
        holiday_date = datetime.fromisoformat(request_dto.holiday_date).date()
        end_date = None
        if request_dto.end_date:
            end_date = datetime.fromisoformat(request_dto.end_date).date()
        
        # Create holiday type
        holiday_type = HolidayType(
            code=request_dto.name.upper().replace(" ", "_")[:10],
            name=request_dto.name,
            category=HolidayCategory(request_dto.holiday_category),
            observance=HolidayObservance(request_dto.holiday_observance),
            recurrence=HolidayRecurrence(request_dto.holiday_recurrence),
            description=request_dto.description
        )
        
        # Create date range
        if request_dto.is_half_day:
            date_range = HolidayDateRange.half_day(
                holiday_date, 
                request_dto.half_day_period
            )
        elif end_date:
            date_range = HolidayDateRange.multi_day(holiday_date, end_date)
        else:
            date_range = HolidayDateRange.single_day(holiday_date)
        
        # Create holiday entity using appropriate factory method
        category = HolidayCategory(request_dto.holiday_category)
        
        if category == HolidayCategory.NATIONAL:
            holiday = PublicHoliday.create_national_holiday(
                name=request_dto.name,
                holiday_date=holiday_date,
                created_by=request_dto.created_by or "system",
                description=request_dto.description,
                notes=request_dto.notes
            )
        elif category == HolidayCategory.RELIGIOUS:
            holiday = PublicHoliday.create_religious_holiday(
                name=request_dto.name,
                holiday_date=holiday_date,
                created_by=request_dto.created_by or "system",
                description=request_dto.description,
                notes=request_dto.notes
            )
        elif category == HolidayCategory.COMPANY:
            holiday = PublicHoliday.create_company_holiday(
                name=request_dto.name,
                holiday_date=holiday_date,
                created_by=request_dto.created_by or "system",
                description=request_dto.description,
                notes=request_dto.notes
            )
        else:
            # For other categories, use the multi-day factory
            holiday = PublicHoliday.create_multi_day_holiday(
                name=request_dto.name,
                start_date=holiday_date,
                end_date=end_date or holiday_date,
                category=category,
                created_by=request_dto.created_by or "system",
                description=request_dto.description,
                notes=request_dto.notes
            )
        
        # Update with custom date range if needed
        if request_dto.is_half_day or (end_date and category in [
            HolidayCategory.NATIONAL, HolidayCategory.RELIGIOUS, HolidayCategory.COMPANY
        ]):
            holiday.date_range = date_range
        
        # Set additional properties
        if request_dto.location_specific:
            holiday.location_specific = request_dto.location_specific
        
        if request_dto.substitute_for:
            holiday.substitute_for = request_dto.substitute_for
        
        return holiday
    
    def _publish_domain_events(self, holiday: PublicHoliday):
        """Publish domain events"""
        try:
            events = holiday.get_domain_events()
            for event in events:
                self.event_publisher.publish(event)
            
            # Clear events after publishing
            holiday.clear_domain_events()
            
            logger.info(f"Published {len(events)} domain events for holiday {holiday.holiday_id}")
            
        except Exception as e:
            logger.error(f"Error publishing domain events: {e}")
            # Don't fail the entire operation for event publishing errors
    
    def _send_notifications(self, holiday: PublicHoliday):
        """Send notifications (optional, non-blocking)"""
        if not self.notification_service:
            return
        
        try:
            # Send creation notification
            self.notification_service.send_holiday_created_notification(holiday)
            
            # Send upcoming holiday notification if it's soon
            if holiday.date_range.is_upcoming() and holiday.date_range.days_until_holiday() <= 7:
                self.notification_service.send_upcoming_holiday_notification(holiday)
            
            logger.info(f"Sent notifications for holiday {holiday.holiday_id}")
            
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
            # Don't fail the entire operation for notification errors 