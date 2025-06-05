"""
SOLID-Compliant Public Holiday Controller
Handles public holiday-related HTTP operations with proper dependency injection
"""

import logging
from typing import List, Optional
from datetime import datetime

from app.application.dto.public_holiday_dto import (
    PublicHolidayCreateRequestDTO,
    PublicHolidayUpdateRequestDTO,
    PublicHolidaySearchFiltersDTO,
    PublicHolidayResponseDTO,
    PublicHolidayImportResultDTO,
    PublicHolidayValidationError,
    PublicHolidayBusinessRuleError,
    PublicHolidayNotFoundError,
    HolidayCategory,
    HolidayObservance,
    HolidayRecurrence
)

logger = logging.getLogger(__name__)


class PublicHolidayController:
    """
    Controller for public holiday operations following SOLID principles.
    
    This controller acts as a facade between the HTTP layer and business logic,
    delegating operations to appropriate use cases.
    """
    
    def __init__(
        self,
        create_use_case=None,
        get_use_case=None,
        update_use_case=None,
        delete_use_case=None,
        import_use_case=None
    ):
        """
        Initialize the controller with use cases.
        
        Args:
            create_use_case: Use case for creating public holidays
            get_use_case: Use case for querying public holidays
            update_use_case: Use case for updating public holidays
            delete_use_case: Use case for deleting public holidays
            import_use_case: Use case for importing public holidays
        """
        self.create_use_case = create_use_case
        self.get_use_case = get_use_case
        self.update_use_case = update_use_case
        self.delete_use_case = delete_use_case
        self.import_use_case = import_use_case
        
        # If use cases are not provided, we'll handle gracefully
        self._initialized = all([
            create_use_case is not None,
            get_use_case is not None,
            update_use_case is not None,
            delete_use_case is not None,
            import_use_case is not None
        ])
        
        if not self._initialized:
            logger.warning("PublicHolidayController initialized without all required use cases")
    
    async def create_public_holiday(self, request: PublicHolidayCreateRequestDTO, employee_id: str, hostname: str) -> PublicHolidayResponseDTO:
        """Create a new public holiday"""
        try:
            logger.info(f"Creating public holiday: {request.name}")
            
            if self.create_use_case:
                return await self.create_use_case.execute(request, employee_id)
            else:
                # Use case not available
                logger.error("Create use case not available")
                raise PublicHolidayBusinessRuleError("Public holiday creation service is not available")
                
        except Exception as e:
            logger.error(f"Error creating public holiday: {e}")
            raise PublicHolidayBusinessRuleError(f"Holiday creation failed: {str(e)}")
    
    async def get_public_holidays(self, filters: PublicHolidaySearchFiltersDTO, hostname: str) -> List[PublicHolidayResponseDTO]:
        """Get public holidays with filters"""
        try:
            logger.info(f"Getting public holidays with filters")
            
            if self.get_use_case:
                # Handle different filter combinations
                if filters.year and filters.month:
                    # Get by specific month and year
                    return await self.get_use_case.get_holidays_by_month(
                        filters.year, filters.month, include_inactive=not filters.active_only
                    )
                elif filters.year:
                    # Get by year
                    return await self.get_use_case.get_holidays_by_year(
                        filters.year, include_inactive=not filters.active_only
                    )
                else:
                    # Get all holidays
                    if filters.active_only:
                        return await self.get_use_case.get_active_holidays()
                    else:
                        return await self.get_use_case.get_all_holidays(include_inactive=True)
            else:
                # Use case not available - return empty list
                logger.warning("Get use case not available, returning empty list")
                return []
                
        except Exception as e:
            logger.error(f"Error getting public holidays: {e}")
            raise PublicHolidayBusinessRuleError(f"Failed to get holidays: {str(e)}")
    
    async def get_public_holiday(self, holiday_id: str, hostname: str) -> PublicHolidayResponseDTO:
        """Get a specific public holiday by ID"""
        try:
            logger.info(f"Getting public holiday: {holiday_id}")
            
            if self.get_use_case:
                return await self.get_use_case.get_holiday_by_id(holiday_id)
            else:
                # Use case not available
                logger.error("Get use case not available")
                raise PublicHolidayNotFoundError(f"Public holiday not found: {holiday_id}")
                
        except Exception as e:
            logger.error(f"Error getting public holiday: {e}")
            raise PublicHolidayBusinessRuleError(f"Failed to get holiday: {str(e)}")
    
    async def update_public_holiday(self, holiday_id: str, request: PublicHolidayUpdateRequestDTO, employee_id: str, hostname: str) -> PublicHolidayResponseDTO:
        """Update an existing public holiday"""
        try:
            logger.info(f"Updating public holiday: {holiday_id}")
            
            if self.update_use_case:
                return await self.update_use_case.execute(holiday_id, request, employee_id)
            else:
                # Use case not available
                logger.error("Update use case not available")
                raise PublicHolidayBusinessRuleError("Public holiday update service is not available")
                
        except Exception as e:
            logger.error(f"Error updating public holiday: {e}")
            raise PublicHolidayBusinessRuleError(f"Holiday update failed: {str(e)}")
    
    async def delete_public_holiday(self, holiday_id: str, employee_id: str, hostname: str) -> None:
        """Delete (deactivate) a public holiday"""
        try:
            logger.info(f"Deleting public holiday: {holiday_id}")
            
            if self.delete_use_case:
                await self.delete_use_case.execute(holiday_id, employee_id)
            else:
                # Use case not available
                logger.error("Delete use case not available")
                raise PublicHolidayBusinessRuleError("Public holiday deletion service is not available")
                
        except Exception as e:
            logger.error(f"Error deleting public holiday: {e}")
            raise PublicHolidayBusinessRuleError(f"Holiday deletion failed: {str(e)}")
    
    async def import_public_holidays(self, file, hostname: str) -> PublicHolidayImportResultDTO:
        """Import public holidays from file"""
        try:
            logger.info(f"Importing public holidays from file: {file.filename}")
            
            if self.import_use_case:
                # Read file content
                content = await file.read()
                return await self.import_use_case.execute(content, file.filename, "system")
            else:
                # Fallback implementation for development/testing
                return PublicHolidayImportResultDTO(
                    total_processed=0,
                    successful_imports=0,
                    failed_imports=0,
                    errors=[],
                    warnings=["Import functionality not available"]
                )
                
        except Exception as e:
            logger.error(f"Error importing public holidays: {e}")
            raise PublicHolidayBusinessRuleError(f"Holiday import failed: {str(e)}")

    async def is_public_holiday(self, date_str: str, hostname: str) -> bool:
        """Check if a specific date is a public holiday"""
        try:
            logger.info(f"Checking if {date_str} is a public holiday")
            
            if self.get_use_case:
                return await self.get_use_case.check_holiday_on_date(date_str)
            else:
                # Fallback implementation for development/testing
                return False
                
        except Exception as e:
            logger.error(f"Error checking holiday on date: {e}")
            raise PublicHolidayBusinessRuleError(f"Holiday check failed: {str(e)}")
    
