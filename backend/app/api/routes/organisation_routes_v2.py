"""
Organisation API Routes
FastAPI route definitions for organisation management
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Path, UploadFile, File, Form
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
    OrganisationConflictError,
    BankDetailsRequestDTO
)
from app.auth.auth_dependencies import CurrentUser, get_current_user
from app.config.dependency_container import get_organisation_controller
from app.api.controllers.organisation_controller import OrganisationController
from app.domain.value_objects.bank_details import BankDetails


logger = logging.getLogger(__name__)

# Create routers - American spelling (primary) and British spelling (alias)
organisation_v2_router = APIRouter(prefix="/api/v2/organisations", tags=["organisations"])  # British spelling alias


# ==================== SHARED ROUTE FUNCTIONS ====================

async def _create_organisation_impl(
    request: CreateOrganisationRequestDTO,
    current_user: CurrentUser,
    controller: OrganisationController
):
    """Shared implementation for create organisation"""
    try:
        response = await controller.create_organisation(
            request=request,
            created_by=current_user.employee_id
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
    current_user: CurrentUser, controller: OrganisationController
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


@organisation_v2_router.post("/", response_model=OrganisationResponseDTO)
async def create_organisation(
    organisation_data: str = Form(..., description="JSON string containing organisation data"),
    logo: Optional[UploadFile] = File(None, description="Organisation logo file (optional)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Create a new organisation (with optional logo upload)"""
    import json
    import os
    from datetime import datetime
    
    try:
        # Parse organisation data from JSON string
        data = json.loads(organisation_data)
        
        # Handle bank details
        bank_details = None
        if "bank_details" in data:
            bank_details = BankDetailsRequestDTO(
                bank_name=data["bank_details"].get("bank_name", ""),
                account_number=data["bank_details"].get("account_number", ""),
                ifsc_code=data["bank_details"].get("ifsc_code", ""),
                account_holder_name=data["bank_details"].get("account_holder_name", ""),
                branch_name=data["bank_details"].get("branch_name"),
                account_type=data["bank_details"].get("account_type")
            )
            # Validate bank details
            errors = bank_details.validate()
            if errors:
                raise HTTPException(status_code=400, detail={"bank_details": errors})

        # Create organisation request DTO
        request = CreateOrganisationRequestDTO(
            name=data.get("name", ""),
            description=data.get("description", ""),
            hostname=data.get("hostname", ""),
            organisation_type=data.get("organisation_type", "private_limited"),
            contact_information=data.get("contact_information", {}),
            address=data.get("address", {}),
            tax_information=data.get("tax_information", {}),
            bank_details=bank_details,
            employee_strength=data.get("employee_strength", 0)
        )

        # Handle logo upload if provided
        logo_path = None
        if logo:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{logo.filename}"
            
            # Ensure uploads directory exists
            os.makedirs("uploads/organisation/logos", exist_ok=True)
            
            # Save file
            logo_path = f"uploads/organisation/logos/{filename}"
            with open(logo_path, "wb") as f:
                f.write(await logo.read())

        # Create organisation
        result = await controller.create_organisation(request, logo_path, current_user)
        return result

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
    current_user: CurrentUser = Depends(get_current_user),
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
    current_user: CurrentUser = Depends(get_current_user),
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
    organisation_id: str,
    request: UpdateOrganisationRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Update an existing organisation"""
    try:
        # Set updated_by
        request.updated_by = current_user.employee_id
        
        # Create bank details value object if bank details fields are provided
        if request.bank_name or request.account_number or request.ifsc_code or request.account_holder_name:
            request.bank_details = BankDetails(
                bank_name=request.bank_name or "",
                account_number=request.account_number or "",
                ifsc_code=request.ifsc_code or "",
                account_holder_name=request.account_holder_name or "",
                branch_name=request.branch_name,
                branch_address=request.branch_address,
                account_type=request.account_type
            )
        
        # Call controller
        return await controller.update_organisation(
            organisation_id=organisation_id,
            request=request
        )
    except ValueError as e:
        logger.error(f"Error validating organisation update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating organisation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@organisation_v2_router.delete("/{organisation_id}")
async def delete_organisation(
    organisation_id: str = Path(..., description="Organisation ID"),
    force: bool = Query(False, description="Force deletion even if business rules prevent it"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Delete an organisation"""
    try:
        success = await controller.delete_organisation(
            organisation_id=organisation_id,
            force=force,
            deleted_by=current_user.employee_id
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


@organisation_v2_router.get("/current/organisation", response_model=OrganisationResponseDTO)
async def get_current_organisation(
    current_user: CurrentUser = Depends(get_current_user),
    controller: OrganisationController = Depends(get_organisation_controller)
):
    """Get current user's organisation based on hostname"""
    try:
        logger.info(f"Getting current organisation for user: {current_user.employee_id} with hostname: {current_user.hostname}")
        
        # Get organisation by hostname
        response = await controller.get_organisation_by_hostname(current_user.hostname)
        
        if not response:
            raise HTTPException(status_code=404, detail="Organisation not found for current user")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current organisation for user {current_user.employee_id}: {e}")
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