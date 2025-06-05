"""
Company Leave API Routes
FastAPI route definitions for company leave management
"""

import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse

from app.application.dto.company_leave_dto import (
    CreateCompanyLeaveRequestDTO,
    UpdateCompanyLeaveRequestDTO,
    CompanyLeaveSearchFiltersDTO,
    CompanyLeaveResponseDTO,
    CompanyLeaveListResponseDTO,
    CompanyLeaveValidationError,
    CompanyLeaveBusinessRuleError,
    CompanyLeaveNotFoundError,
    CompanyLeaveConflictError
)
from app.auth.auth_dependencies import CurrentUser, get_current_user
from app.config.dependency_container import get_company_leave_controller
from app.api.controllers.company_leave_controller import CompanyLeaveController


logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/company-leaves", tags=["company-leaves"])


@router.post("/", response_model=CompanyLeaveResponseDTO)
async def create_company_leave(
    request: CreateCompanyLeaveRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Create a new company leave"""
    return await controller.create_company_leave(request, current_user)


@router.get("/", response_model=CompanyLeaveListResponseDTO)
async def list_company_leaves(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    accrual_type: Optional[str] = Query(None, description="Filter by accrual type"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """List company leaves with optional filters and pagination"""
    return await controller.list_company_leaves(
        CompanyLeaveSearchFiltersDTO(
            page=page,
            page_size=page_size,
            is_active=is_active,
            accrual_type=accrual_type,
            sort_by=sort_by,
            sort_order=sort_order
        )
    )


@router.get("/{company_leave_id}", response_model=CompanyLeaveResponseDTO)
async def get_company_leave(
    company_leave_id: str = Path(..., description="Company Leave ID"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Get company leave by ID"""
    try:
        response = await controller.get_company_leave_by_id(company_leave_id)
        
        if not response:
            raise HTTPException(status_code=404, detail="Company leave not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company leave {company_leave_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{company_leave_id}", response_model=CompanyLeaveResponseDTO)
async def update_company_leave(
    company_leave_id: str = Path(..., description="Company Leave ID"),
    request: UpdateCompanyLeaveRequestDTO = None,
    current_user: CurrentUser = Depends(get_current_user),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Update an existing company leave"""
    try:
        response = await controller.update_company_leave(
            company_leave_id=company_leave_id,
            request=request,
            updated_by=current_user.employee_id
        )
        
        return response
        
    except CompanyLeaveNotFoundError as e:
        logger.warning(f"Company leave not found for update: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except CompanyLeaveValidationError as e:
        logger.warning(f"Validation error updating company leave: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except CompanyLeaveConflictError as e:
        logger.warning(f"Conflict error updating company leave: {e}")
        raise HTTPException(status_code=409, detail={"error": "conflict_error", "message": str(e)})
    
    except CompanyLeaveBusinessRuleError as e:
        logger.warning(f"Business rule error updating company leave: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error updating company leave {company_leave_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{company_leave_id}")
async def delete_company_leave(
    company_leave_id: str = Path(..., description="Company Leave ID"),
    force: bool = Query(False, description="Force deletion even if business rules prevent it"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Delete company leave"""
    try:
        await controller.delete_company_leave(
            company_leave_id=company_leave_id,
            force=force,
            deleted_by=current_user.employee_id
        )
        
        return {"message": "Company leave deleted successfully"}
        
    except CompanyLeaveNotFoundError as e:
        logger.warning(f"Company leave not found for deletion: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except CompanyLeaveBusinessRuleError as e:
        logger.warning(f"Business rule error deleting company leave: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error deleting company leave {company_leave_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "company-leaves"} 