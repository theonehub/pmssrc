"""
Organization API Controllers
FastAPI controllers for organization management
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse

from app.application.use_cases.organization.create_organization_use_case import CreateOrganizationUseCase
from app.application.use_cases.organization.update_organization_use_case import UpdateOrganizationUseCase
from app.application.use_cases.organization.get_organization_use_case import GetOrganizationUseCase
from app.application.use_cases.organization.list_organizations_use_case import ListOrganizationsUseCase
from app.application.use_cases.organization.delete_organization_use_case import DeleteOrganizationUseCase
from app.application.dto.organization_dto import (
    CreateOrganizationRequestDTO,
    UpdateOrganizationRequestDTO,
    OrganizationStatusUpdateRequestDTO,
    OrganizationSearchFiltersDTO,
    OrganizationResponseDTO,
    OrganizationSummaryDTO,
    OrganizationListResponseDTO,
    OrganizationStatisticsDTO,
    OrganizationAnalyticsDTO,
    OrganizationHealthCheckDTO,
    OrganizationValidationError,
    OrganizationBusinessRuleError,
    OrganizationNotFoundError,
    OrganizationConflictError
)
from app.auth.auth_dependencies import get_current_user


logger = logging.getLogger(__name__)

# Create router
organization_router = APIRouter(prefix="/api/organizations", tags=["organizations"])


class OrganizationController:
    """
    Controller for organization management operations.
    
    Follows SOLID principles:
    - SRP: Each endpoint handles a single operation
    - OCP: Extensible through dependency injection
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused on organization operations
    - DIP: Depends on use case abstractions
    """
    
    def __init__(
        self,
        create_use_case: CreateOrganizationUseCase,
        update_use_case: UpdateOrganizationUseCase,
        get_use_case: GetOrganizationUseCase,
        list_use_case: ListOrganizationsUseCase,
        delete_use_case: DeleteOrganizationUseCase
    ):
        self.create_use_case = create_use_case
        self.update_use_case = update_use_case
        self.get_use_case = get_use_case
        self.list_use_case = list_use_case
        self.delete_use_case = delete_use_case


# Global controller instance (will be injected)
controller: Optional[OrganizationController] = None


def get_organization_controller() -> OrganizationController:
    """Dependency injection for organization controller"""
    if controller is None:
        raise HTTPException(status_code=500, detail="Organization controller not initialized")
    return controller


# ==================== ORGANIZATION CRUD ENDPOINTS ====================

@organization_router.post("/", response_model=OrganizationResponseDTO)
async def create_organization(
    request: CreateOrganizationRequestDTO,
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Create a new organization"""
    try:
        logger.info(f"Creating organization: {request.name} by {current_user.get('employee_id')}")
        
        response = await controller.create_use_case.execute(
            request=request,
            created_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except OrganizationValidationError as e:
        logger.warning(f"Validation error creating organization: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except OrganizationConflictError as e:
        logger.warning(f"Conflict error creating organization: {e}")
        raise HTTPException(status_code=409, detail={"error": "conflict_error", "message": str(e)})
    
    except OrganizationBusinessRuleError as e:
        logger.warning(f"Business rule error creating organization: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error creating organization: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.get("/", response_model=OrganizationListResponseDTO)
async def list_organizations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    name: Optional[str] = Query(None, description="Filter by organization name"),
    organization_type: Optional[str] = Query(None, description="Filter by organization type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    country: Optional[str] = Query(None, description="Filter by country"),
    created_after: Optional[datetime] = Query(None, description="Filter by creation date (after)"),
    created_before: Optional[datetime] = Query(None, description="Filter by creation date (before)"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """List organizations with optional filters and pagination"""
    try:
        logger.info(f"Listing organizations with filters")
        
        # Create search filters
        filters = OrganizationSearchFiltersDTO(
            name=name,
            organization_type=organization_type,
            status=status,
            city=city,
            state=state,
            country=country,
            created_after=created_after,
            created_before=created_before,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit
        )
        
        response = await controller.list_use_case.execute(filters)
        
        return response
        
    except Exception as e:
        logger.error(f"Error listing organizations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.get("/{organization_id}", response_model=OrganizationResponseDTO)
async def get_organization(
    organization_id: str = Path(..., description="Organization ID"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Get organization by ID"""
    try:
        logger.info(f"Getting organization: {organization_id}")
        
        response = await controller.get_use_case.execute_by_id(organization_id)
        
        if not response:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.put("/{organization_id}", response_model=OrganizationResponseDTO)
async def update_organization(
    organization_id: str = Path(..., description="Organization ID"),
    request: UpdateOrganizationRequestDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Update an existing organization"""
    try:
        logger.info(f"Updating organization: {organization_id} by {current_user.get('employee_id')}")
        
        response = await controller.update_use_case.execute(
            organization_id=organization_id,
            request=request,
            updated_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except OrganizationNotFoundError as e:
        logger.warning(f"Organization not found for update: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except OrganizationValidationError as e:
        logger.warning(f"Validation error updating organization: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except OrganizationConflictError as e:
        logger.warning(f"Conflict error updating organization: {e}")
        raise HTTPException(status_code=409, detail={"error": "conflict_error", "message": str(e)})
    
    except OrganizationBusinessRuleError as e:
        logger.warning(f"Business rule error updating organization: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error updating organization {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.delete("/{organization_id}")
async def delete_organization(
    organization_id: str = Path(..., description="Organization ID"),
    force: bool = Query(False, description="Force deletion even if business rules prevent it"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Delete an organization"""
    try:
        logger.info(f"Deleting organization: {organization_id} by {current_user.get('employee_id')} (force: {force})")
        
        success = await controller.delete_use_case.execute(
            organization_id=organization_id,
            force=force,
            deleted_by=current_user.get("employee_id", "unknown")
        )
        
        if success:
            return JSONResponse(
                status_code=200,
                content={"message": "Organization deleted successfully"}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to delete organization")
        
    except OrganizationNotFoundError as e:
        logger.warning(f"Organization not found for deletion: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except OrganizationBusinessRuleError as e:
        logger.warning(f"Business rule error deleting organization: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error deleting organization {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== ORGANIZATION STATUS ENDPOINTS ====================

@organization_router.patch("/{organization_id}/status", response_model=OrganizationResponseDTO)
async def update_organization_status(
    organization_id: str = Path(..., description="Organization ID"),
    request: OrganizationStatusUpdateRequestDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Update organization status"""
    try:
        logger.info(f"Updating organization status: {organization_id} to {request.status} by {current_user.get('employee_id')}")
        
        response = await controller.update_use_case.execute_status_update(
            organization_id=organization_id,
            request=request,
            updated_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except OrganizationNotFoundError as e:
        logger.warning(f"Organization not found for status update: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except OrganizationValidationError as e:
        logger.warning(f"Validation error updating organization status: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except OrganizationBusinessRuleError as e:
        logger.warning(f"Business rule error updating organization status: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error updating organization status {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== ORGANIZATION LOOKUP ENDPOINTS ====================

@organization_router.get("/by-name/{name}", response_model=OrganizationResponseDTO)
async def get_organization_by_name(
    name: str = Path(..., description="Organization name"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Get organization by name"""
    try:
        logger.info(f"Getting organization by name: {name}")
        
        response = await controller.get_use_case.execute_by_name(name)
        
        if not response:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization by name {name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.get("/by-hostname/{hostname}", response_model=OrganizationResponseDTO)
async def get_organization_by_hostname(
    hostname: str = Path(..., description="Organization hostname"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Get organization by hostname"""
    try:
        logger.info(f"Getting organization by hostname: {hostname}")
        
        response = await controller.get_use_case.execute_by_hostname(hostname)
        
        if not response:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization by hostname {hostname}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.get("/by-pan/{pan_number}", response_model=OrganizationResponseDTO)
async def get_organization_by_pan_number(
    pan_number: str = Path(..., description="Organization PAN number"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Get organization by PAN number"""
    try:
        logger.info(f"Getting organization by PAN: {pan_number}")
        
        response = await controller.get_use_case.execute_by_pan_number(pan_number)
        
        if not response:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting organization by PAN {pan_number}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== ORGANIZATION EMPLOYEE CAPACITY ENDPOINTS ====================

@organization_router.post("/{organization_id}/increment-employee-usage", response_model=OrganizationResponseDTO)
async def increment_employee_usage(
    organization_id: str = Path(..., description="Organization ID"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Increment employee usage count"""
    try:
        logger.info(f"Incrementing employee usage for organization: {organization_id}")
        
        response = await controller.update_use_case.execute_increment_employee_usage(
            organization_id=organization_id,
            updated_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except OrganizationNotFoundError as e:
        logger.warning(f"Organization not found for employee usage increment: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except OrganizationBusinessRuleError as e:
        logger.warning(f"Business rule error incrementing employee usage: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error incrementing employee usage {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.post("/{organization_id}/decrement-employee-usage", response_model=OrganizationResponseDTO)
async def decrement_employee_usage(
    organization_id: str = Path(..., description="Organization ID"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Decrement employee usage count"""
    try:
        logger.info(f"Decrementing employee usage for organization: {organization_id}")
        
        response = await controller.update_use_case.execute_decrement_employee_usage(
            organization_id=organization_id,
            updated_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except OrganizationNotFoundError as e:
        logger.warning(f"Organization not found for employee usage decrement: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except OrganizationBusinessRuleError as e:
        logger.warning(f"Business rule error decrementing employee usage: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error decrementing employee usage {organization_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== ORGANIZATION ANALYTICS ENDPOINTS ====================

@organization_router.get("/analytics/statistics", response_model=OrganizationStatisticsDTO)
async def get_organization_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Get organization statistics"""
    try:
        logger.info(f"Getting organization statistics (start: {start_date}, end: {end_date})")
        
        response = await controller.list_use_case.execute_statistics(
            start_date=start_date,
            end_date=end_date
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting organization statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.get("/analytics/health", response_model=OrganizationHealthCheckDTO)
async def get_organization_health(
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Get organization system health check"""
    try:
        logger.info("Getting organization system health")
        
        # This would need to be implemented in the use case
        # For now, return a basic health check
        return OrganizationHealthCheckDTO(
            status="healthy",
            total_organizations=0,
            active_organizations=0,
            inactive_organizations=0,
            suspended_organizations=0,
            capacity_utilization_percentage=0.0,
            last_check_time=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error getting organization health: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== ORGANIZATION VALIDATION ENDPOINTS ====================

@organization_router.post("/validate", response_model=dict)
async def validate_organization_data(
    request: CreateOrganizationRequestDTO,
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Validate organization data without creating"""
    try:
        logger.info("Validating organization data")
        
        # This would need to be implemented in the use case
        # For now, return basic validation
        return {"valid": True, "errors": []}
        
    except OrganizationValidationError as e:
        return {"valid": False, "errors": [str(e)]}
    
    except Exception as e:
        logger.error(f"Error validating organization data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.get("/check-availability/name/{name}")
async def check_name_availability(
    name: str = Path(..., description="Organization name to check"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Check if organization name is available"""
    try:
        logger.info(f"Checking name availability: {name}")
        
        exists = await controller.get_use_case.execute_exists_by_name(name)
        
        return {"available": not exists, "name": name}
        
    except Exception as e:
        logger.error(f"Error checking name availability {name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.get("/check-availability/hostname/{hostname}")
async def check_hostname_availability(
    hostname: str = Path(..., description="Hostname to check"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Check if hostname is available"""
    try:
        logger.info(f"Checking hostname availability: {hostname}")
        
        exists = await controller.get_use_case.execute_exists_by_hostname(hostname)
        
        return {"available": not exists, "hostname": hostname}
        
    except Exception as e:
        logger.error(f"Error checking hostname availability {hostname}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@organization_router.get("/check-availability/pan/{pan_number}")
async def check_pan_availability(
    pan_number: str = Path(..., description="PAN number to check"),
    current_user: dict = Depends(get_current_user),
    controller: OrganizationController = Depends(get_organization_controller)
):
    """Check if PAN number is available"""
    try:
        logger.info(f"Checking PAN availability: {pan_number}")
        
        exists = await controller.get_use_case.execute_exists_by_pan_number(pan_number)
        
        return {"available": not exists, "pan_number": pan_number}
        
    except Exception as e:
        logger.error(f"Error checking PAN availability {pan_number}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== HEALTH CHECK ENDPOINT ====================

@organization_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "organization"}


# ==================== CONTROLLER INITIALIZATION ====================

def initialize_organization_controller(
    create_use_case: CreateOrganizationUseCase,
    update_use_case: UpdateOrganizationUseCase,
    get_use_case: GetOrganizationUseCase,
    list_use_case: ListOrganizationsUseCase,
    delete_use_case: DeleteOrganizationUseCase
):
    """Initialize the global organization controller instance"""
    global controller
    controller = OrganizationController(
        create_use_case=create_use_case,
        update_use_case=update_use_case,
        get_use_case=get_use_case,
        list_use_case=list_use_case,
        delete_use_case=delete_use_case
    )
    logger.info("Organization controller initialized successfully") 