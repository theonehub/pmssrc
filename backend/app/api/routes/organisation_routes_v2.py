"""
Organisation API Routes
FastAPI route definitions for organisation management
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse

from app.application.dto.organisation_dto import (
    CreateOrganisationRequestDTO,
    UpdateOrganisationRequestDTO,
    OrganisationSearchFiltersDTO,
    OrganisationResponseDTO,
    OrganisationListResponseDTO,
    OrganisationStatisticsDTO,
    OrganisationHealthCheckDTO,
    OrganisationValidationError,
    OrganisationBusinessRuleError,
    OrganisationNotFoundError,
    OrganisationConflictError
)
from app.auth.auth_dependencies import get_current_user
from app.config.dependency_container import get_organisation_controller
from app.api.controllers.organisation_controller import OrganisationController


logger = logging.getLogger(__name__)

# Create routers - American spelling (primary) and British spelling (alias)
organisation_v2_router = APIRouter(prefix="/api/v2/organisations", tags=["organisations"])  # British spelling alias


# ==================== SHARED ROUTE FUNCTIONS ====================

async def _create_organisation_impl(
    request: CreateOrganisationRequestDTO,
    current_user: dict,
    controller: OrganisationController
):
    """Shared implementation for create organisation"""
    try:
        response = await controller.create_organisation(
            request=request,
            created_by=current_user.get("employee_id", "unknown")
        )
        return response
        
    except OrganisationValidationError as e:
        logger.warning(f"Validation error creating organisation: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except OrganisationConflictError as e:
        logger.warning(f"Conflict error creating organisation: {e}")
        raise HTTPException(status_code=409, detail={"error": "conflict_error", "message": str(e)})
    
    except OrganisationBusinessRuleError as e:
        logger.warning(f"Business rule error creating organisation: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error creating organisation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def _list_organisations_impl(
    skip: int, limit: int, name: Optional[str], organisation_type: Optional[str],
    status: Optional[str], city: Optional[str], state: Optional[str], country: Optional[str],
    created_after: Optional[datetime], created_before: Optional[datetime],
    sort_by: Optional[str], sort_order: Optional[str],
    current_user: dict, controller: OrganisationController
):
    """Shared implementation for list organisations"""
    try:
        # Convert skip/limit to page/page_size for the DTO
        page = (skip // limit) + 1 if limit > 0 else 1
        page_size = min(limit, 100)  # Cap at 100 per DTO validation
        
        # Create search filters with correct pagination parameters
        filters = OrganisationSearchFiltersDTO(
            name=name,
            organisation_type=organisation_type,
            status=status,
            city=city,
            state=state,
            country=country,
            created_after=created_after,
            created_before=created_before,
            sort_by=sort_by or "name",
            sort_order=sort_order or "asc",
            page=page,
            page_size=page_size
        )
        
        response = await controller.list_organisations(filters)
        return response
        
    except Exception as e:
        logger.error(f"Error listing organisations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== AMERICAN SPELLING ROUTES (/api/v2/organisations) ====================

@organisation_v2_router.post("/", response_model=OrganisationResponseDTO)
async def create_organisation(
    request: CreateOrganisationRequestDTO,
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Create a new organisation"""
    return await _create_organisation_impl(request, current_user, controller)


@organisation_v2_router.get("/", response_model=OrganisationListResponseDTO)
async def list_organisations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    name: Optional[str] = Query(None, description="Filter by organisation name"),
    organisation_type: Optional[str] = Query(None, description="Filter by organisation type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    country: Optional[str] = Query(None, description="Filter by country"),
    created_after: Optional[datetime] = Query(None, description="Filter by creation date (after)"),
    created_before: Optional[datetime] = Query(None, description="Filter by creation date (before)"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """List organisations with optional filters and pagination"""
    return await _list_organisations_impl(
        skip, limit, name, organisation_type, status, city, state, country,
        created_after, created_before, sort_by, sort_order, current_user, controller
    )


# ==================== BRITISH SPELLING ROUTES (/api/v2/organisations) ====================

@organisation_v2_router.post("/", response_model=OrganisationResponseDTO)
async def create_organisation(
    request: CreateOrganisationRequestDTO,
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Create a new organisation (British spelling alias)"""
    return await _create_organisation_impl(request, current_user, controller)


@organisation_v2_router.get("/", response_model=OrganisationListResponseDTO)
async def list_organisations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    name: Optional[str] = Query(None, description="Filter by organisation name"),
    organisation_type: Optional[str] = Query(None, description="Filter by organisation type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    country: Optional[str] = Query(None, description="Filter by country"),
    created_after: Optional[datetime] = Query(None, description="Filter by creation date (after)"),
    created_before: Optional[datetime] = Query(None, description="Filter by creation date (before)"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """List organisations with optional filters and pagination (British spelling alias)"""
    return await _list_organisations_impl(
        skip, limit, name, organisation_type, status, city, state, country,
        created_after, created_before, sort_by, sort_order, current_user, controller
    )


# ==================== REMAINING ROUTES (American spelling only for brevity) ====================

@organisation_v2_router.get("/{organisation_id}", response_model=OrganisationResponseDTO)
async def get_organisation(
    organisation_id: str = Path(..., description="Organisation ID"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Get organisation by ID"""
    try:
        response = await controller.get_organisation_by_id(organisation_id)
        
        if not response:
            raise HTTPException(status_code=404, detail="Organisation not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organisation {organisation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organisation_v2_router.put("/{organisation_id}", response_model=OrganisationResponseDTO)
async def update_organisation(
    organisation_id: str = Path(..., description="Organisation ID"),
    request: UpdateOrganisationRequestDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Update an existing organisation"""
    try:
        response = await controller.update_organisation(
            organisation_id=organisation_id,
            request=request,
            updated_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except OrganisationNotFoundError as e:
        logger.warning(f"Organisation not found for update: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except OrganisationValidationError as e:
        logger.warning(f"Validation error updating organisation: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except OrganisationConflictError as e:
        logger.warning(f"Conflict error updating organisation: {e}")
        raise HTTPException(status_code=409, detail={"error": "conflict_error", "message": str(e)})
    
    except OrganisationBusinessRuleError as e:
        logger.warning(f"Business rule error updating organisation: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error updating organisation {organisation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organisation_v2_router.delete("/{organisation_id}")
async def delete_organisation(
    organisation_id: str = Path(..., description="Organisation ID"),
    force: bool = Query(False, description="Force deletion even if business rules prevent it"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Delete an organisation"""
    try:
        success = await controller.delete_organisation(
            organisation_id=organisation_id,
            force=force,
            deleted_by=current_user.get("employee_id", "unknown")
        )
        
        if success:
            return JSONResponse(
                status_code=200,
                content={"message": "Organisation deleted successfully"}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to delete organisation")
        
    except OrganisationNotFoundError as e:
        logger.warning(f"Organisation not found for deletion: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except OrganisationBusinessRuleError as e:
        logger.warning(f"Business rule error deleting organisation: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error deleting organisation {organisation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ==================== ORGANISATION LOOKUP ENDPOINTS ====================

@organisation_v2_router.get("/by-name/{name}", response_model=OrganisationResponseDTO)
async def get_organisation_by_name(
    name: str = Path(..., description="Organisation name"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Get organisation by name"""
    try:
        response = await controller.get_organisation_by_name(name)
        
        if not response:
            raise HTTPException(status_code=404, detail="Organisation not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organisation by name {name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organisation_v2_router.get("/by-hostname/{hostname}", response_model=OrganisationResponseDTO)
async def get_organisation_by_hostname(
    hostname: str = Path(..., description="Organisation hostname"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Get organisation by hostname"""
    try:
        response = await controller.get_organisation_by_hostname(hostname)
        
        if not response:
            raise HTTPException(status_code=404, detail="Organisation not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organisation by hostname {hostname}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organisation_v2_router.get("/by-pan/{pan_number}", response_model=OrganisationResponseDTO)
async def get_organisation_by_pan_number(
    pan_number: str = Path(..., description="Organisation PAN number"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Get organisation by PAN number"""
    try:
        response = await controller.get_organisation_by_pan_number(pan_number)
        
        if not response:
            raise HTTPException(status_code=404, detail="Organisation not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organisation by PAN {pan_number}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== ORGANISATION EMPLOYEE CAPACITY ENDPOINTS ====================

@organisation_v2_router.post("/{organisation_id}/increment-employee-usage", response_model=OrganisationResponseDTO)
async def increment_employee_usage(
    organisation_id: str = Path(..., description="Organisation ID"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Increment employee usage count"""
    try:
        response = await controller.increment_employee_usage(
            organisation_id=organisation_id,
            updated_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except OrganisationNotFoundError as e:
        logger.warning(f"Organisation not found for employee usage increment: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except OrganisationBusinessRuleError as e:
        logger.warning(f"Business rule error incrementing employee usage: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error incrementing employee usage {organisation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organisation_v2_router.post("/{organisation_id}/decrement-employee-usage", response_model=OrganisationResponseDTO)
async def decrement_employee_usage(
    organisation_id: str = Path(..., description="Organisation ID"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Decrement employee usage count"""
    try:
        response = await controller.decrement_employee_usage(
            organisation_id=organisation_id,
            updated_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except OrganisationNotFoundError as e:
        logger.warning(f"Organisation not found for employee usage decrement: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except OrganisationBusinessRuleError as e:
        logger.warning(f"Business rule error decrementing employee usage: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error decrementing employee usage {organisation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== ORGANISATION ANALYTICS ENDPOINTS ====================

@organisation_v2_router.get("/analytics/statistics", response_model=OrganisationStatisticsDTO)
async def get_organisation_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Get organisation statistics"""
    try:
        response = await controller.get_organisation_statistics(
            start_date=start_date,
            end_date=end_date
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting organisation statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organisation_v2_router.get("/analytics/health", response_model=OrganisationHealthCheckDTO)
async def get_organisation_health(
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Get organisation system health check"""
    try:
        logger.info("Getting organisation system health")
        
        # This would need to be implemented in the use case
        # For now, return a basic health check
        return OrganisationHealthCheckDTO(
            status="healthy",
            total_organisations=0,
            active_organisations=0,
            inactive_organisations=0,
            suspended_organisations=0,
            capacity_utilization_percentage=0.0,
            last_check_time=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting organisation health: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== ORGANISATION VALIDATION ENDPOINTS ====================

@organisation_v2_router.post("/validate", response_model=dict)
async def validate_organisation_data(
    request: CreateOrganisationRequestDTO,
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Validate organisation data without creating"""
    try:
        logger.info("Validating organisation data")
        
        # This would need to be implemented in the use case
        # For now, return basic validation
        return {"valid": True, "errors": []}
        
    except OrganisationValidationError as e:
        return {"valid": False, "errors": [str(e)]}
    
    except Exception as e:
        logger.error(f"Error validating organisation data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organisation_v2_router.get("/check-availability/name/{name}")
async def check_name_availability(
    name: str = Path(..., description="Organisation name to check"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Check if organisation name is available"""
    try:
        exists = await controller.check_name_exists(name)
        return {"available": not exists, "name": name}
        
    except Exception as e:
        logger.error(f"Error checking name availability {name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organisation_v2_router.get("/check-availability/hostname/{hostname}")
async def check_hostname_availability(
    hostname: str = Path(..., description="Hostname to check"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Check if hostname is available"""
    try:
        exists = await controller.check_hostname_exists(hostname)
        return {"available": not exists, "hostname": hostname}
        
    except Exception as e:
        logger.error(f"Error checking hostname availability {hostname}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organisation_v2_router.get("/check-availability/pan/{pan_number}")
async def check_pan_availability(
    pan_number: str = Path(..., description="PAN number to check"),
    current_user: dict = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Check if PAN number is available"""
    try:
        exists = await controller.check_pan_exists(pan_number)
        return {"available": not exists, "pan_number": pan_number}
        
    except Exception as e:
        logger.error(f"Error checking PAN availability {pan_number}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== HEALTH CHECK ENDPOINT ====================

@organisation_v2_router.get("/health")
async def health_check():
    """Health check for organisation system (American spelling)"""
    return {"status": "healthy", "system": "organisation", "spelling": "American"}


@organisation_v2_router.get("/health")
async def health_check_british():
    """Health check for organisation system (British spelling)"""
    return {"status": "healthy", "system": "organisation", "spelling": "British"} 