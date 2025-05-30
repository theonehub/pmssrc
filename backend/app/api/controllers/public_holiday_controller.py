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
    
    async def create_public_holiday(self, request: PublicHolidayCreateRequestDTO, emp_id: str, hostname: str) -> PublicHolidayResponseDTO:
        """Create a new public holiday"""
        try:
            logger.info(f"Creating public holiday: {request.name}")
            
            if self.create_use_case:
                return await self.create_use_case.execute(request, emp_id, hostname)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_response(request)
                
        except Exception as e:
            logger.error(f"Error creating public holiday: {e}")
            raise PublicHolidayBusinessRuleError(f"Holiday creation failed: {str(e)}")
    
    async def get_public_holidays(self, filters: PublicHolidaySearchFiltersDTO, hostname: str) -> List[PublicHolidayResponseDTO]:
        """Get public holidays with filters"""
        try:
            logger.info(f"Getting public holidays with filters")
            
            if self.get_use_case:
                return await self.get_use_case.execute(filters, hostname)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_list(filters)
                
        except Exception as e:
            logger.error(f"Error getting public holidays: {e}")
            raise PublicHolidayBusinessRuleError(f"Failed to get holidays: {str(e)}")
    
    async def get_public_holiday(self, holiday_id: str, hostname: str) -> PublicHolidayResponseDTO:
        """Get a specific public holiday by ID"""
        try:
            logger.info(f"Getting public holiday: {holiday_id}")
            
            if self.get_use_case:
                return await self.get_use_case.get_by_id(holiday_id, hostname)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_single_response(holiday_id)
                
        except Exception as e:
            logger.error(f"Error getting public holiday: {e}")
            raise PublicHolidayBusinessRuleError(f"Failed to get holiday: {str(e)}")
    
    async def update_public_holiday(self, holiday_id: str, request: PublicHolidayUpdateRequestDTO, emp_id: str, hostname: str) -> PublicHolidayResponseDTO:
        """Update an existing public holiday"""
        try:
            logger.info(f"Updating public holiday: {holiday_id}")
            
            if self.update_use_case:
                return await self.update_use_case.execute(holiday_id, request, emp_id, hostname)
            else:
                # Fallback implementation for development/testing
                return self._create_mock_updated_response(holiday_id, request)
                
        except Exception as e:
            logger.error(f"Error updating public holiday: {e}")
            raise PublicHolidayBusinessRuleError(f"Holiday update failed: {str(e)}")
    
    async def delete_public_holiday(self, holiday_id: str, emp_id: str, hostname: str) -> None:
        """Delete (deactivate) a public holiday"""
        try:
            logger.info(f"Deleting public holiday: {holiday_id}")
            
            if self.delete_use_case:
                await self.delete_use_case.execute(holiday_id, emp_id, hostname)
            else:
                # Fallback implementation for development/testing
                logger.info(f"Mock deletion of public holiday: {holiday_id}")
                
        except Exception as e:
            logger.error(f"Error deleting public holiday: {e}")
            raise PublicHolidayBusinessRuleError(f"Holiday deletion failed: {str(e)}")
    
    # Private helper methods for fallback implementations
    
    def _create_mock_response(self, request: PublicHolidayCreateRequestDTO) -> PublicHolidayResponseDTO:
        """Create a mock public holiday response for development/testing"""
        current_time = datetime.now()
        
        return PublicHolidayResponseDTO(
            id=f"holiday_{request.name.lower().replace(' ', '_')}_{current_time.strftime('%Y%m%d')}",
            name=request.name,
            holiday_date=request.holiday_date,
            description=request.description or "",
            category=request.category,
            observance=request.observance,
            recurrence=request.recurrence,
            is_active=True,
            created_at=current_time,
            updated_at=current_time,
            created_by="SYSTEM",
            updated_by="SYSTEM"
        )
    
    def _create_mock_list(self, filters: PublicHolidaySearchFiltersDTO) -> List[PublicHolidayResponseDTO]:
        """Create mock public holiday list for development/testing"""
        # Return empty list for now - can be enhanced later
        logger.info(f"Returning empty public holiday list for filters: {filters}")
        return []
    
    def _create_mock_single_response(self, holiday_id: str) -> PublicHolidayResponseDTO:
        """Create mock single public holiday response for development/testing"""
        current_time = datetime.now()
        
        return PublicHolidayResponseDTO(
            id=holiday_id,
            name="Mock Holiday",
            holiday_date=current_time.date(),
            description="Mock public holiday for testing",
            category=HolidayCategory.NATIONAL,
            observance=HolidayObservance.MANDATORY,
            recurrence=HolidayRecurrence.ANNUAL,
            is_active=True,
            created_at=current_time,
            updated_at=current_time,
            created_by="SYSTEM",
            updated_by="SYSTEM"
        )
    
    def _create_mock_updated_response(self, holiday_id: str, request: PublicHolidayUpdateRequestDTO) -> PublicHolidayResponseDTO:
        """Create mock updated public holiday response for development/testing"""
        current_time = datetime.now()
        
        return PublicHolidayResponseDTO(
            id=holiday_id,
            name=request.name or "Updated Mock Holiday",
            holiday_date=request.holiday_date or current_time.date(),
            description=request.description or "Updated mock public holiday",
            category=request.category or HolidayCategory.NATIONAL,
            observance=request.observance or HolidayObservance.MANDATORY,
            recurrence=request.recurrence or HolidayRecurrence.ANNUAL,
            is_active=request.is_active if request.is_active is not None else True,
            created_at=current_time,
            updated_at=current_time,
            created_by="SYSTEM",
            updated_by="SYSTEM"
        ) 