"""
Public Holiday Controller Implementation
SOLID-compliant controller for public holiday HTTP operations
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import HTTPException

from app.application.interfaces.services.public_holiday_service import PublicHolidayService
from app.application.dto.public_holiday_dto import (
    CreatePublicHolidayRequestDTO, UpdatePublicHolidayRequestDTO, PublicHolidaySearchFiltersDTO,
    PublicHolidayResponseDTO, PublicHolidayListResponseDTO, ImportPublicHolidayRequestDTO,
    PublicHolidayValidationError, PublicHolidayBusinessRuleError, PublicHolidayNotFoundError
)
from app.auth.auth_dependencies import CurrentUser

logger = logging.getLogger(__name__)

class PublicHolidayController:
    """
    Public holiday controller following SOLID principles.
    
    - SRP: Only handles HTTP request/response concerns
    - OCP: Can be extended with new endpoints
    - LSP: Can be substituted with other controllers
    - ISP: Focused interface for public holiday HTTP operations
    - DIP: Depends on abstractions (PublicHolidayService)
    """
    
    def __init__(self, public_holiday_service: PublicHolidayService):
        """Initialize controller with dependencies."""
        self.public_holiday_service = public_holiday_service
    
    async def create_public_holiday(
        self, 
        request: CreatePublicHolidayRequestDTO, 
        current_user: CurrentUser
    ) -> PublicHolidayResponseDTO:
        """Create a new public holiday."""
        try:
            logger.info(f"Creating public holiday in organisation: {current_user.hostname}")
            return await self.public_holiday_service.create_public_holiday(request, current_user)
        except PublicHolidayValidationError as e:
            logger.warning(f"Validation error creating public holiday: {e}")
            raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
        except PublicHolidayBusinessRuleError as e:
            logger.warning(f"Business rule error creating public holiday: {e}")
            raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
        except Exception as e:
            logger.error(f"Error creating public holiday in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_public_holiday_by_id(
        self, 
        holiday_id: str, 
        current_user: CurrentUser
    ) -> PublicHolidayResponseDTO:
        """Get public holiday by ID."""
        try:
            holiday = await self.public_holiday_service.get_public_holiday_by_id(holiday_id, current_user)
            if not holiday:
                raise HTTPException(status_code=404, detail="Public holiday not found")
            return holiday
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting public holiday {holiday_id} in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def list_public_holidays(
        self, 
        filters: PublicHolidaySearchFiltersDTO, 
        current_user: CurrentUser
    ) -> PublicHolidayListResponseDTO:
        """List public holidays with filters."""
        try:
            return await self.public_holiday_service.list_public_holidays(filters, current_user)
        except Exception as e:
            logger.error(f"Error listing public holidays in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def update_public_holiday(
        self,
        holiday_id: str,
        request: UpdatePublicHolidayRequestDTO,
        current_user: CurrentUser
    ) -> PublicHolidayResponseDTO:
        """Update public holiday."""
        try:
            return await self.public_holiday_service.update_public_holiday(holiday_id, request, current_user)
        except PublicHolidayNotFoundError as e:
            logger.warning(f"Public holiday not found for update: {e}")
            raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
        except PublicHolidayValidationError as e:
            logger.warning(f"Validation error updating public holiday: {e}")
            raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
        except PublicHolidayBusinessRuleError as e:
            logger.warning(f"Business rule error updating public holiday: {e}")
            raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error updating public holiday {holiday_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def delete_public_holiday(
        self,
        holiday_id: str,
        force: bool,
        current_user: CurrentUser
    ) -> bool:
        """Delete public holiday."""
        try:
            return await self.public_holiday_service.delete_public_holiday(holiday_id, force, current_user)
        except PublicHolidayNotFoundError as e:
            logger.warning(f"Public holiday not found for deletion: {e}")
            raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
        except PublicHolidayBusinessRuleError as e:
            logger.warning(f"Business rule error deleting public holiday: {e}")
            raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
        except Exception as e:
            logger.error(f"Unexpected error deleting public holiday {holiday_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def import_public_holidays(
        self,
        request: ImportPublicHolidayRequestDTO,
        current_user: CurrentUser
    ) -> List[PublicHolidayResponseDTO]:
        """Import public holidays."""
        try:
            return await self.public_holiday_service.import_public_holidays(request, current_user)
        except PublicHolidayValidationError as e:
            logger.warning(f"Validation error importing public holidays: {e}")
            raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
        except Exception as e:
            logger.error(f"Error importing public holidays in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def get_holidays_by_date_range(
        self,
        start_date: str,
        end_date: str,
        current_user: CurrentUser
    ) -> List[PublicHolidayResponseDTO]:
        """Get holidays by date range."""
        try:
            from datetime import datetime
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            return await self.public_holiday_service.get_holidays_by_date_range(start_dt, end_dt, current_user)
        except ValueError as e:
            logger.warning(f"Invalid date format: {e}")
            raise HTTPException(status_code=400, detail={"error": "invalid_date_format", "message": "Date must be in YYYY-MM-DD format"})
        except Exception as e:
            logger.error(f"Error getting holidays by date range in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    async def check_holiday_on_date(
        self,
        date_str: str,
        current_user: CurrentUser
    ) -> Dict[str, Any]:
        """Check if a specific date is a public holiday."""
        try:
            from datetime import datetime
            check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Get holidays for the specific date
            holidays = await self.public_holiday_service.get_holidays_by_date_range(
                check_date, check_date, current_user
            )
            
            is_holiday = len(holidays) > 0
            holiday_info = holidays[0] if holidays else None
            
            return {
                "date": date_str,
                "is_holiday": is_holiday,
                "holiday": holiday_info.dict() if holiday_info else None
            }
        except ValueError as e:
            logger.warning(f"Invalid date format: {e}")
            raise HTTPException(status_code=400, detail={"error": "invalid_date_format", "message": "Date must be in YYYY-MM-DD format"})
        except Exception as e:
            logger.error(f"Error checking holiday on date in organisation {current_user.hostname}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
