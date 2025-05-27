"""
SOLID-Compliant Public Holiday Routes
Clean API layer following SOLID principles
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
from datetime import datetime

from api.controllers.public_holiday_controller import PublicHolidayController
from application.dto.public_holiday_dto import (
    PublicHolidayCreateRequestDTO,
    PublicHolidayUpdateRequestDTO,
    PublicHolidaySearchFiltersDTO,
    PublicHolidayResponseDTO,
    PublicHolidayImportResultDTO,
    PublicHolidayValidationError,
    PublicHolidayBusinessRuleError,
    PublicHolidayNotFoundError
)
from auth.auth import extract_emp_id, extract_hostname, role_checker

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/public-holidays", tags=["Public Holidays V2 (SOLID)"])


def get_public_holiday_controller() -> PublicHolidayController:
    """Dependency injection for public holiday controller"""
    from config.dependency_container import get_dependency_container
    container = get_dependency_container()
    return container.get_public_holiday_controller()


# ==================== PUBLIC HOLIDAY ENDPOINTS ====================

@router.post("/", response_model=PublicHolidayResponseDTO)
async def create_public_holiday(
    request: PublicHolidayCreateRequestDTO,
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Create a new public holiday"""
    try:
        logger.info(f"Creating public holiday: {request.name} by {current_emp_id}")
        
        response = await controller.create_public_holiday(request, current_emp_id, hostname)
        
        return response
        
    except PublicHolidayValidationError as e:
        logger.warning(f"Validation error creating public holiday: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except PublicHolidayBusinessRuleError as e:
        logger.warning(f"Business rule error creating public holiday: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error creating public holiday: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[PublicHolidayResponseDTO])
async def get_public_holidays(
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
    active_only: bool = Query(True, description="Return only active holidays"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    hostname: str = Depends(extract_hostname),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Get public holidays with optional filters"""
    try:
        logger.info(f"Getting public holidays with filters: year={year}, month={month}")
        
        filters = PublicHolidaySearchFiltersDTO(
            year=year,
            month=month,
            active_only=active_only,
            skip=skip,
            limit=limit
        )
        
        response = await controller.get_public_holidays(filters, hostname)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting public holidays: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{holiday_id}", response_model=PublicHolidayResponseDTO)
async def get_public_holiday(
    holiday_id: str = Path(..., description="Public holiday ID"),
    hostname: str = Depends(extract_hostname),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Get a specific public holiday by ID"""
    try:
        logger.info(f"Getting public holiday: {holiday_id}")
        
        response = await controller.get_public_holiday(holiday_id, hostname)
        
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
    holiday_id: str = Path(..., description="Public holiday ID"),
    request: PublicHolidayUpdateRequestDTO = None,
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Update an existing public holiday"""
    try:
        logger.info(f"Updating public holiday: {holiday_id} by {current_emp_id}")
        
        response = await controller.update_public_holiday(
            holiday_id, request, current_emp_id, hostname
        )
        
        return response
        
    except PublicHolidayNotFoundError as e:
        logger.warning(f"Public holiday not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except PublicHolidayValidationError as e:
        logger.warning(f"Validation error updating public holiday: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except PublicHolidayBusinessRuleError as e:
        logger.warning(f"Business rule error updating public holiday: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error updating public holiday: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{holiday_id}")
async def delete_public_holiday(
    holiday_id: str = Path(..., description="Public holiday ID"),
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Delete (deactivate) a public holiday"""
    try:
        logger.info(f"Deleting public holiday: {holiday_id} by {current_emp_id}")
        
        await controller.delete_public_holiday(holiday_id, current_emp_id, hostname)
        
        return {"message": "Public holiday deleted successfully"}
        
    except PublicHolidayNotFoundError as e:
        logger.warning(f"Public holiday not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except PublicHolidayBusinessRuleError as e:
        logger.warning(f"Business rule error deleting public holiday: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error deleting public holiday: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/import", response_model=PublicHolidayImportResultDTO)
async def import_public_holidays(
    file: UploadFile = File(...),
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Import public holidays from Excel file"""
    try:
        logger.info(f"Importing public holidays from file: {file.filename} by {current_emp_id}")
        
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")
        
        response = await controller.import_public_holidays(file, current_emp_id, hostname)
        
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
    hostname: str = Depends(extract_hostname),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Check if a specific date is a public holiday"""
    try:
        logger.info(f"Checking if {date} is a public holiday")
        
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        is_holiday = await controller.is_public_holiday(date, hostname)
        
        return {
            "date": date,
            "is_public_holiday": is_holiday,
            "checked_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking public holiday for {date}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/month/{month}/year/{year}", response_model=List[PublicHolidayResponseDTO])
async def get_public_holidays_by_month(
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2000, le=3000, description="Year"),
    hostname: str = Depends(extract_hostname),
    controller: PublicHolidayController = Depends(get_public_holiday_controller)
):
    """Get public holidays for a specific month and year"""
    try:
        logger.info(f"Getting public holidays for {month}/{year}")
        
        filters = PublicHolidaySearchFiltersDTO(
            month=month,
            year=year,
            active_only=True
        )
        
        response = await controller.get_public_holidays(filters, hostname)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting public holidays for {month}/{year}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "public_holidays_v2"} 