"""
SOLID-Compliant Company Leave Routes
Clean API layer following SOLID principles
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
from datetime import datetime

from api.controllers.company_leave_controller import CompanyLeaveController
from application.dto.company_leave_dto import (
    CompanyLeaveCreateRequestDTO,
    CompanyLeaveUpdateRequestDTO,
    CompanyLeaveSearchFiltersDTO,
    CompanyLeaveResponseDTO,
    CompanyLeaveValidationError,
    CompanyLeaveBusinessRuleError,
    CompanyLeaveNotFoundError
)
from auth.auth import extract_emp_id, extract_hostname, role_checker

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/company-leaves", tags=["Company Leaves V2 (SOLID)"])


def get_company_leave_controller() -> CompanyLeaveController:
    """Dependency injection for company leave controller"""
    from config.dependency_container import get_dependency_container
    container = get_dependency_container()
    return container.get_company_leave_controller()


# ==================== COMPANY LEAVE ENDPOINTS ====================

@router.post("/", response_model=CompanyLeaveResponseDTO)
async def create_company_leave(
    request: CompanyLeaveCreateRequestDTO,
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Create a new company leave policy"""
    try:
        logger.info(f"Creating company leave: {request.leave_type} by {current_emp_id}")
        
        response = await controller.create_company_leave(request, current_emp_id, hostname)
        
        return response
        
    except CompanyLeaveValidationError as e:
        logger.warning(f"Validation error creating company leave: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except CompanyLeaveBusinessRuleError as e:
        logger.warning(f"Business rule error creating company leave: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error creating company leave: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/", response_model=List[CompanyLeaveResponseDTO])
async def get_company_leaves(
    leave_type: Optional[str] = Query(None, description="Filter by leave type"),
    active_only: bool = Query(True, description="Return only active leave policies"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    hostname: str = Depends(extract_hostname),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Get company leave policies with optional filters"""
    try:
        logger.info(f"Getting company leaves with filters: leave_type={leave_type}")
        
        filters = CompanyLeaveSearchFiltersDTO(
            leave_type=leave_type,
            active_only=active_only,
            skip=skip,
            limit=limit
        )
        
        response = await controller.get_company_leaves(filters, hostname)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting company leaves: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{leave_id}", response_model=CompanyLeaveResponseDTO)
async def get_company_leave(
    leave_id: str = Path(..., description="Company leave ID"),
    hostname: str = Depends(extract_hostname),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Get a specific company leave policy by ID"""
    try:
        logger.info(f"Getting company leave: {leave_id}")
        
        response = await controller.get_company_leave(leave_id, hostname)
        
        if not response:
            raise HTTPException(status_code=404, detail="Company leave policy not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company leave {leave_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{leave_id}", response_model=CompanyLeaveResponseDTO)
async def update_company_leave(
    request: CompanyLeaveUpdateRequestDTO,
    leave_id: str = Path(..., description="Company leave ID"),
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Update an existing company leave policy"""
    try:
        logger.info(f"Updating company leave: {leave_id} by {current_emp_id}")
        
        response = await controller.update_company_leave(
            leave_id, request, current_emp_id, hostname
        )
        
        return response
        
    except CompanyLeaveNotFoundError as e:
        logger.warning(f"Company leave not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except CompanyLeaveValidationError as e:
        logger.warning(f"Validation error updating company leave: {e}")
        raise HTTPException(status_code=400, detail={"error": "validation_error", "message": str(e)})
    
    except CompanyLeaveBusinessRuleError as e:
        logger.warning(f"Business rule error updating company leave: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error updating company leave: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{leave_id}")
async def delete_company_leave(
    leave_id: str = Path(..., description="Company leave ID"),
    current_emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Delete (deactivate) a company leave policy"""
    try:
        logger.info(f"Deleting company leave: {leave_id} by {current_emp_id}")
        
        await controller.delete_company_leave(leave_id, current_emp_id, hostname)
        
        return {"message": "Company leave policy deleted successfully"}
        
    except CompanyLeaveNotFoundError as e:
        logger.warning(f"Company leave not found: {e}")
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": str(e)})
    
    except CompanyLeaveBusinessRuleError as e:
        logger.warning(f"Business rule error deleting company leave: {e}")
        raise HTTPException(status_code=422, detail={"error": "business_rule_error", "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error deleting company leave: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/types/available", response_model=List[str])
async def get_available_leave_types(
    hostname: str = Depends(extract_hostname),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Get all available leave types for the organization"""
    try:
        logger.info("Getting available leave types")
        
        response = await controller.get_available_leave_types(hostname)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting available leave types: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/employee/{emp_id}/entitlements", response_model=List[CompanyLeaveResponseDTO])
async def get_employee_leave_entitlements(
    emp_id: str = Path(..., description="Employee ID"),
    hostname: str = Depends(extract_hostname),
    current_emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Get leave entitlements for a specific employee"""
    try:
        logger.info(f"Getting leave entitlements for employee: {emp_id}")
        
        # Check if user can access this employee's data
        if role not in ["admin", "superadmin"] and emp_id != current_emp_id:
            # For managers, check if they manage this employee
            if role == "manager":
                # This would need to be implemented based on your manager-employee relationship logic
                pass
            else:
                raise HTTPException(status_code=403, detail="Access denied")
        
        response = await controller.get_employee_leave_entitlements(emp_id, hostname)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employee leave entitlements: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/my/entitlements", response_model=List[CompanyLeaveResponseDTO])
async def get_my_leave_entitlements(
    hostname: str = Depends(extract_hostname),
    current_emp_id: str = Depends(extract_emp_id),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Get my leave entitlements"""
    try:
        logger.info(f"Getting leave entitlements for current user: {current_emp_id}")
        
        response = await controller.get_employee_leave_entitlements(current_emp_id, hostname)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting my leave entitlements: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/usage", response_model=dict)
async def get_leave_usage_analytics(
    year: Optional[int] = Query(None, description="Filter by year"),
    leave_type: Optional[str] = Query(None, description="Filter by leave type"),
    hostname: str = Depends(extract_hostname),
    current_emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    controller: CompanyLeaveController = Depends(get_company_leave_controller)
):
    """Get leave usage analytics"""
    try:
        logger.info(f"Getting leave usage analytics for year: {year}, leave_type: {leave_type}")
        
        response = await controller.get_leave_usage_analytics(
            year=year,
            leave_type=leave_type,
            manager_id=current_emp_id if role == "manager" else None,
            hostname=hostname
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting leave usage analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "company_leaves_v2"} 