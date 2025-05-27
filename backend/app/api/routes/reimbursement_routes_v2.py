"""
SOLID-Compliant Reimbursement Routes
Clean API layer following SOLID principles
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, Body, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from api.controllers.reimbursement_controller import ReimbursementController
from application.dto.reimbursement_dto import (
    ReimbursementRequestCreateDTO,
    ReimbursementTypeCreateRequestDTO,
    ReimbursementApprovalDTO,
    ReimbursementPaymentDTO,
    ReimbursementSearchFiltersDTO,
    ReimbursementResponseDTO,
    ReimbursementTypeResponseDTO,
    ReimbursementValidationError,
    ReimbursementBusinessRuleError,
    ReimbursementNotFoundError
)
from auth.auth import extract_hostname, extract_emp_id, role_checker
from config.dependency_container import get_reimbursement_controller

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/reimbursements", tags=["Reimbursements V2"])


def get_controller() -> ReimbursementController:
    """Get reimbursement controller instance"""
    return get_reimbursement_controller()


# Reimbursement Request Endpoints

@router.post("/requests", response_model=ReimbursementResponseDTO)
async def create_reimbursement_request(
    request_data: ReimbursementRequestCreateDTO,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Create a new reimbursement request.
    
    - **reimbursement_type_id**: ID of the reimbursement type
    - **amount**: Amount to be reimbursed
    - **description**: Description of the expense
    - **receipt_url**: Optional receipt file URL
    """
    try:
        # Set employee ID from authentication
        request_data.employee_id = emp_id
        
        result = await controller.create_reimbursement_request(request_data, hostname)
        return result
        
    except ReimbursementValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ReimbursementBusinessRuleError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.error(f"Error creating reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/requests/with-file", response_model=ReimbursementResponseDTO)
async def create_reimbursement_request_with_file(
    reimbursement_type_id: str = Form(...),
    amount: float = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Create a new reimbursement request with file upload.
    
    - **reimbursement_type_id**: ID of the reimbursement type
    - **amount**: Amount to be reimbursed
    - **description**: Description of the expense
    - **file**: Receipt file (image or PDF)
    """
    try:
        # Create DTO from form data
        request_data = ReimbursementRequestCreateDTO(
            employee_id=emp_id,
            reimbursement_type_id=reimbursement_type_id,
            amount=amount,
            description=description
        )
        
        result = await controller.create_reimbursement_request_with_file(
            request_data, file, hostname
        )
        return result
        
    except ReimbursementValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ReimbursementBusinessRuleError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.error(f"Error creating reimbursement request with file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/requests/my", response_model=List[ReimbursementResponseDTO])
async def get_my_reimbursement_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Get current user's reimbursement requests.
    
    - **status**: Optional status filter (pending, approved, rejected, paid)
    - **limit**: Maximum number of requests to return
    - **offset**: Number of requests to skip for pagination
    """
    try:
        filters = ReimbursementSearchFiltersDTO(
            employee_id=emp_id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        result = await controller.get_reimbursement_requests(filters, hostname)
        return result
        
    except Exception as e:
        logger.error(f"Error getting user reimbursement requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/requests/pending", response_model=List[ReimbursementResponseDTO])
async def get_pending_reimbursement_requests(
    limit: int = Query(50, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Get pending reimbursement requests for approval.
    
    - **limit**: Maximum number of requests to return
    - **offset**: Number of requests to skip for pagination
    
    Managers see requests from their team members.
    Admins see all pending requests.
    """
    try:
        # For managers, filter by their managed employees
        # For admin/superadmin, show all pending requests
        manager_id = emp_id if role == "manager" else None
        
        filters = ReimbursementSearchFiltersDTO(
            status="pending",
            manager_id=manager_id,
            limit=limit,
            offset=offset
        )
        
        result = await controller.get_reimbursement_requests(filters, hostname)
        return result
        
    except Exception as e:
        logger.error(f"Error getting pending reimbursement requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/requests/approved", response_model=List[ReimbursementResponseDTO])
async def get_approved_reimbursement_requests(
    limit: int = Query(50, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Get approved reimbursement requests.
    
    - **limit**: Maximum number of requests to return
    - **offset**: Number of requests to skip for pagination
    
    Managers see requests from their team members.
    Admins see all approved requests.
    """
    try:
        # For managers, filter by their managed employees
        # For admin/superadmin, show all approved requests
        manager_id = emp_id if role == "manager" else None
        
        filters = ReimbursementSearchFiltersDTO(
            status="approved",
            manager_id=manager_id,
            limit=limit,
            offset=offset
        )
        
        result = await controller.get_reimbursement_requests(filters, hostname)
        return result
        
    except Exception as e:
        logger.error(f"Error getting approved reimbursement requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/requests/{request_id}", response_model=ReimbursementResponseDTO)
async def get_reimbursement_request(
    request_id: str,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Get a specific reimbursement request by ID.
    
    - **request_id**: ID of the reimbursement request
    """
    try:
        result = await controller.get_reimbursement_request(request_id, emp_id, hostname)
        return result
        
    except ReimbursementNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Error getting reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/requests/{request_id}", response_model=ReimbursementResponseDTO)
async def update_reimbursement_request(
    request_id: str,
    request_data: ReimbursementRequestCreateDTO,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Update a reimbursement request.
    
    - **request_id**: ID of the reimbursement request
    - **request_data**: Updated request data
    """
    try:
        # Set employee ID from authentication
        request_data.employee_id = emp_id
        
        result = await controller.update_reimbursement_request(
            request_id, request_data, emp_id, hostname
        )
        return result
        
    except ReimbursementNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ReimbursementValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except ReimbursementBusinessRuleError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.error(f"Error updating reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/requests/{request_id}/approve", response_model=ReimbursementResponseDTO)
async def approve_reimbursement_request(
    request_id: str,
    approval_data: ReimbursementApprovalDTO,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Approve a reimbursement request.
    
    - **request_id**: ID of the reimbursement request
    - **approval_data**: Approval details and comments
    """
    try:
        # Set approver ID from authentication
        approval_data.approved_by = emp_id
        
        result = await controller.approve_reimbursement_request(
            request_id, approval_data, hostname
        )
        return result
        
    except ReimbursementNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ReimbursementBusinessRuleError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.error(f"Error approving reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/requests/{request_id}/reject", response_model=ReimbursementResponseDTO)
async def reject_reimbursement_request(
    request_id: str,
    rejection_reason: str = Body(..., embed=True),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Reject a reimbursement request.
    
    - **request_id**: ID of the reimbursement request
    - **rejection_reason**: Reason for rejection
    """
    try:
        result = await controller.reject_reimbursement_request(
            request_id, rejection_reason, emp_id, hostname
        )
        return result
        
    except ReimbursementNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ReimbursementBusinessRuleError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.error(f"Error rejecting reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/requests/{request_id}")
async def delete_reimbursement_request(
    request_id: str,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Delete a reimbursement request.
    
    - **request_id**: ID of the reimbursement request
    """
    try:
        await controller.delete_reimbursement_request(request_id, emp_id, hostname)
        return {"message": "Reimbursement request deleted successfully"}
        
    except ReimbursementNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ReimbursementBusinessRuleError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        logger.error(f"Error deleting reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Reimbursement Type Endpoints

@router.post("/types", response_model=ReimbursementTypeResponseDTO)
async def create_reimbursement_type(
    type_data: ReimbursementTypeCreateRequestDTO,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Create a new reimbursement type.
    
    - **name**: Name of the reimbursement type
    - **category**: Category (travel, medical, food, etc.)
    - **max_limit**: Optional maximum limit per request
    - **description**: Optional description
    """
    try:
        result = await controller.create_reimbursement_type(type_data, emp_id, hostname)
        return result
        
    except ReimbursementValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error creating reimbursement type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/types", response_model=List[ReimbursementTypeResponseDTO])
async def get_reimbursement_types(
    active_only: bool = Query(True, description="Return only active types"),
    hostname: str = Depends(extract_hostname),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Get all reimbursement types.
    
    - **active_only**: Whether to return only active types
    """
    try:
        result = await controller.get_reimbursement_types(active_only, hostname)
        return result
        
    except Exception as e:
        logger.error(f"Error getting reimbursement types: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/types/{type_id}", response_model=ReimbursementTypeResponseDTO)
async def get_reimbursement_type(
    type_id: str,
    hostname: str = Depends(extract_hostname),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Get a specific reimbursement type by ID.
    
    - **type_id**: ID of the reimbursement type
    """
    try:
        result = await controller.get_reimbursement_type(type_id, hostname)
        return result
        
    except ReimbursementNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Error getting reimbursement type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/types/{type_id}", response_model=ReimbursementTypeResponseDTO)
async def update_reimbursement_type(
    type_id: str,
    type_data: ReimbursementTypeCreateRequestDTO,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Update a reimbursement type.
    
    - **type_id**: ID of the reimbursement type
    - **type_data**: Updated type data
    """
    try:
        result = await controller.update_reimbursement_type(
            type_id, type_data, emp_id, hostname
        )
        return result
        
    except ReimbursementNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ReimbursementValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error updating reimbursement type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/types/{type_id}")
async def delete_reimbursement_type(
    type_id: str,
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Delete (deactivate) a reimbursement type.
    
    - **type_id**: ID of the reimbursement type
    """
    try:
        await controller.delete_reimbursement_type(type_id, emp_id, hostname)
        return {"message": "Reimbursement type deleted successfully"}
        
    except ReimbursementNotFoundError as e:
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Error deleting reimbursement type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Analytics and Reporting Endpoints

@router.get("/analytics/summary")
async def get_reimbursement_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_controller)
):
    """
    Get reimbursement analytics and summary.
    
    - **start_date**: Optional start date for filtering
    - **end_date**: Optional end date for filtering
    
    Managers see analytics for their team.
    Admins see organization-wide analytics.
    """
    try:
        # For managers, filter by their managed employees
        manager_id = emp_id if role == "manager" else None
        
        result = await controller.get_reimbursement_analytics(
            start_date, end_date, manager_id, hostname
        )
        return result
        
    except Exception as e:
        logger.error(f"Error getting reimbursement analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 