"""
Public Holiday API Routes
FastAPI route definitions for public holiday management
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, UploadFile, File
from fastapi.responses import JSONResponse
from datetime import date, datetime

from app.api.controllers.public_holiday_controller import PublicHolidayController
from app.application.dto.public_holiday_dto import (
    CreatePublicHolidayRequestDTO,
    UpdatePublicHolidayRequestDTO,
    PublicHolidaySearchFiltersDTO,
    PublicHolidayResponseDTO,
    PublicHolidayListResponseDTO,
    ImportPublicHolidayRequestDTO,
    PublicHolidayValidationError,
    PublicHolidayBusinessRuleError,
    PublicHolidayNotFoundError
)
from app.auth.auth_dependencies import CurrentUser, get_current_user, require_role
from app.config.dependency_container import get_dependency_container

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/public-holidays", tags=["public-holidays-v2"])

def get_public_holiday_controller() -> PublicHolidayController:
    """Get public holiday controller instance."""
    try:
        container = get_dependency_container()
        return container.get_public_holiday_controller()
    except Exception as e:
        logger.error(f"Could not get public holiday controller from container: {e}")
        raise HTTPException(status_code=500, detail="Service initialization error")

# Health check endpoint
@router.get("/health")
async def health_check(
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
) -> Dict[str, str]:
    """Health check for public holiday service."""
    return {"status": "healthy", "service": "public_holiday_service"}

# CRUD endpoints
@router.post("/", response_model=PublicHolidayResponseDTO)
async def create_public_holiday(
    request: CreatePublicHolidayRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
) -> PublicHolidayResponseDTO:
    """Create a new public holiday."""
    try:
        logger.info(f"Creating public holiday by {current_user.employee_id} in organisation {current_user.hostname}")
        return await controller.create_public_holiday(request, current_user)
    except PublicHolidayValidationError as e:
        logger.warning(f"Validation error creating public holiday: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    except PublicHolidayBusinessRuleError as e:
        logger.warning(f"Business rule error creating public holiday: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error creating public holiday: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=PublicHolidayListResponseDTO)
async def list_public_holidays(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    sort_by: Optional[str] = Query("date", description="Sort field"),
    sort_order: Optional[str] = Query("asc", description="Sort order (asc/desc)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """List public holidays with optional filters and pagination"""
    try:
        filters = PublicHolidaySearchFiltersDTO(
            page=(skip // limit) + 1 if limit > 0 else 1,
            page_size=min(limit, 100),
            year=year,
            month=month,
            is_active=is_active,
            sort_by=sort_by or "date",
            sort_order=sort_order or "asc"
        )
        
        return await controller.list_public_holidays(filters, current_user)
    except Exception as e:
        logger.error(f"Error listing public holidays: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{holiday_id}", response_model=PublicHolidayResponseDTO)
async def get_public_holiday(
    holiday_id: str = Path(..., description="Public Holiday ID"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Get public holiday by ID"""
    try:
        response = await controller.get_public_holiday_by_id(holiday_id, current_user)
        if not response:
            raise HTTPException(status_code=404, detail="Public holiday not found")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting public holiday {holiday_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{holiday_id}", response_model=PublicHolidayResponseDTO)
async def update_public_holiday(
    holiday_id: str = Path(..., description="Public Holiday ID"),
    request: UpdatePublicHolidayRequestDTO = None,
    current_user: CurrentUser = Depends(get_current_user),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Update an existing public holiday"""
    try:
        return await controller.update_public_holiday(holiday_id, request, current_user)
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

@router.delete("/{holiday_id}")
async def delete_public_holiday(
    holiday_id: str = Path(..., description="Public Holiday ID"),
    force: bool = Query(False, description="Force deletion even if business rules prevent it"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Delete public holiday"""
    try:
        await controller.delete_public_holiday(holiday_id, force, current_user)
        return {"message": "Public holiday deleted successfully"}
    except PublicHolidayNotFoundError as e:
        logger.warning(f"Public holiday not found for deletion: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    except PublicHolidayBusinessRuleError as e:
        logger.warning(f"Business rule error deleting public holiday: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error deleting public holiday {holiday_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/import", response_model=List[PublicHolidayResponseDTO])
async def import_public_holidays(
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Import public holidays from Excel file"""
    try:
        logger.info(f"Importing public holidays from file: {file.filename} by {current_user.employee_id}")
        
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Only Excel (.xlsx, .xls) and CSV files are supported")
        
        # Read file content
        content = await file.read()
        
        # Create import request DTO
        import_request = ImportPublicHolidayRequestDTO(
            file_content=content,
            file_name=file.filename,
            file_type=file.filename.split('.')[-1].lower()
        )
        
        response = await controller.import_public_holidays(import_request, current_user)
        
        return response
        
    except PublicHolidayValidationError as e:
        logger.warning(f"Validation error importing public holidays: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    except Exception as e:
        logger.error(f"Unexpected error importing public holidays: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/check/{date}", response_model=dict)
async def check_public_holiday(
    date: str = Path(..., description="Date in YYYY-MM-DD format"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Check if a specific date is a public holiday"""
    try:
        logger.info(f"Checking if {date} is a public holiday")
        
        response = await controller.check_holiday_on_date(date, current_user)
        
        return response
        
    except Exception as e:
        logger.error(f"Error checking public holiday on date {date}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/range/{start_date}/{end_date}", response_model=List[PublicHolidayResponseDTO])
async def get_public_holidays_by_date_range(
    start_date: str = Path(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Path(..., description="End date in YYYY-MM-DD format"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Get public holidays within a date range"""
    try:
        logger.info(f"Getting public holidays from {start_date} to {end_date}")
        
        response = await controller.get_holidays_by_date_range(start_date, end_date, current_user)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting public holidays by date range: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 