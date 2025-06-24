"""
SOLID-Compliant Reimbursement Routes v2
Clean architecture implementation of reimbursement HTTP endpoints
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from datetime import date, datetime

from app.api.controllers.reimbursement_controller import ReimbursementController
from app.application.dto.reimbursement_dto import (
    ReimbursementRequestCreateDTO,
    ReimbursementRequestUpdateDTO,
    ReimbursementApprovalDTO,
    ReimbursementSearchFiltersDTO,
    ReimbursementResponseDTO,
    ReimbursementSummaryDTO,
    ReimbursementStatisticsDTO,
    ReimbursementValidationError,
    ReimbursementBusinessRuleError,
    ReimbursementNotFoundError,
    ReimbursementTypeCreateRequestDTO,
    ReimbursementTypeUpdateRequestDTO,
    ReimbursementTypeResponseDTO,
    ReimbursementTypeOptionsDTO,
    ReimbursementRejectionDTO,
    ReimbursementPaymentDTO,
    ReimbursementReceiptUploadDTO
)
from app.config.dependency_container import get_dependency_container
from app.auth.auth_dependencies import CurrentUser, get_current_user, require_role

# Import auth functions - use the new auth dependencies approach
from app.auth.auth import extract_employee_id, extract_hostname, role_checker

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/reimbursements", tags=["reimbursements-v2"])

def get_reimbursement_controller() -> ReimbursementController:
    """Get reimbursement controller instance."""
    try:
        container = get_dependency_container()
        return container.get_reimbursement_controller()
    except Exception as e:
        logger.warning(f"Could not get reimbursement controller from container: {e}")
        return ReimbursementController()


# Health check endpoint
@router.get("/health")
async def health_check(
    controller: ReimbursementController = Depends(get_reimbursement_controller)
) -> Dict[str, Any]:
    """Health check for reimbursement service."""
    return await controller.health_check()

# Reimbursement CRUD endpoints
@router.get("", response_model=List[ReimbursementSummaryDTO])
@router.get("/", response_model=List[ReimbursementSummaryDTO])
async def get_reimbursements(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
) -> List[ReimbursementSummaryDTO]:
    """Get reimbursement requests with optional filtering."""
    try:
        filters = ReimbursementSearchFiltersDTO(
            employee_id=current_user.employee_id,
            status=status,
            page=offset // limit + 1,
            page_size=limit
        )
        
        result = await controller.list_reimbursement_requests(filters, current_user)
        return result.reimbursements
        
    except Exception as e:
        logger.error(f"Error getting reimbursement requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("", response_model=ReimbursementResponseDTO)
async def create_reimbursement(
    request: ReimbursementRequestCreateDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
) -> ReimbursementResponseDTO:
    """Create a new reimbursement request."""
    try:
        logger.info(f"Creating reimbursement request for employee {current_user.employee_id}")
        return await controller.create_reimbursement_request(request, current_user)
    except Exception as e:
        logger.error(f"Error creating reimbursement: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Reimbursement Request Endpoints

@router.post("/requests", response_model=ReimbursementResponseDTO)
async def create_reimbursement_request(
    request_data: ReimbursementRequestCreateDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Create a new reimbursement request.
    
    - **reimbursement_type_id**: ID of the reimbursement type
    - **amount**: Amount to be reimbursed
    - **description**: Description of the expense
    - **receipt_url**: Optional receipt file URL
    """
    try:
        result = await controller.create_reimbursement_request(request_data, current_user)
        return result
        
    except ReimbursementValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ReimbursementBusinessRuleError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/requests/with-file", response_model=ReimbursementResponseDTO)
async def create_reimbursement_request_with_file(
    reimbursement_type_id: str = Form(...),
    amount: float = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
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
            employee_id=current_user.employee_id,
            reimbursement_type_id=reimbursement_type_id,
            amount=amount,
            description=description
        )
        
        result = await controller.create_reimbursement_request_with_file(
            request_data, file, current_user
        )
        return result
        
    except ReimbursementValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ReimbursementBusinessRuleError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating reimbursement request with file: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/requests/my", response_model=List[ReimbursementSummaryDTO])
async def get_my_reimbursement_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Get current user's reimbursement requests.
    
    - **status**: Optional status filter (pending, approved, rejected, paid)
    - **limit**: Maximum number of requests to return
    - **offset**: Number of requests to skip for pagination
    """
    try:
        filters = ReimbursementSearchFiltersDTO(
            employee_id=current_user.employee_id,
            status=status,
            page=offset // limit + 1,
            page_size=limit
        )
        
        result = await controller.list_reimbursement_requests(filters, current_user)
        return result.reimbursements
        
    except Exception as e:
        logger.error(f"Error getting user reimbursement requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/requests/pending", response_model=List[ReimbursementSummaryDTO])
async def get_pending_reimbursement_requests(
    limit: int = Query(50, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
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
        manager_id = current_user.employee_id if role == "manager" else None
        
        # Get requests with pending statuses: draft, submitted, under_review
        pending_statuses = ["draft", "submitted", "under_review"]
        all_pending_requests = []
        
        for status in pending_statuses:
            # Get all pages for this status
            page = 1
            while True:
                filters = ReimbursementSearchFiltersDTO(
                    status=status,
                    approved_by=manager_id,
                    page=page,
                    page_size=100  # Maximum allowed page size
                )
                
                result = await controller.list_reimbursement_requests(filters, current_user)
                all_pending_requests.extend(result.reimbursements)
                
                # Break if we got fewer results than page size (last page)
                if len(result.reimbursements) < 100:
                    break
                page += 1
        
        # Apply pagination to combined results
        start_idx = offset
        end_idx = offset + limit
        paginated_requests = all_pending_requests[start_idx:end_idx]
        
        return paginated_requests
        
    except Exception as e:
        logger.error(f"Error getting pending reimbursement requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/requests/approved", response_model=List[ReimbursementSummaryDTO])
async def get_approved_reimbursement_requests(
    limit: int = Query(50, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
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
        manager_id = current_user.employee_id if role == "manager" else None
        
        filters = ReimbursementSearchFiltersDTO(
            status="approved",
            approved_by=manager_id,
            page=offset // limit + 1,
            page_size=limit
        )
        
        result = await controller.list_reimbursement_requests(filters, current_user)
        return result.reimbursements
        
    except Exception as e:
        logger.error(f"Error getting approved reimbursement requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Legacy endpoints for frontend compatibility
@router.get("/pending", response_model=List[ReimbursementSummaryDTO])
async def get_pending_reimbursements_legacy(
    limit: int = Query(50, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Get pending reimbursement requests for approval (legacy endpoint).
    
    - **limit**: Maximum number of requests to return
    - **offset**: Number of requests to skip for pagination
    
    Managers see requests from their team members.
    Admins see all pending requests.
    """
    try:
        # For managers, filter by their managed employees
        # For admin/superadmin, show all pending requests
        manager_id = current_user.employee_id if role == "manager" else None
        
        # Get requests with pending statuses: draft, submitted, under_review
        pending_statuses = ["draft", "submitted", "under_review"]
        all_pending_requests = []
        
        for status in pending_statuses:
            # Get all pages for this status
            page = 1
            while True:
                filters = ReimbursementSearchFiltersDTO(
                    status=status,
                    approved_by=manager_id,
                    page=page,
                    page_size=100  # Maximum allowed page size
                )
                
                result = await controller.list_reimbursement_requests(filters, current_user)
                all_pending_requests.extend(result.reimbursements)
                
                # Break if we got fewer results than page size (last page)
                if len(result.reimbursements) < 100:
                    break
                page += 1
        
        # Apply pagination to combined results
        start_idx = offset
        end_idx = offset + limit
        paginated_requests = all_pending_requests[start_idx:end_idx]
        
        return paginated_requests
        
    except Exception as e:
        logger.error(f"Error getting pending reimbursement requests (legacy): {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/approved", response_model=List[ReimbursementSummaryDTO])
async def get_approved_reimbursements_legacy(
    limit: int = Query(50, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Get approved reimbursement requests (legacy endpoint).
    
    - **limit**: Maximum number of requests to return
    - **offset**: Number of requests to skip for pagination
    
    Managers see requests from their team members.
    Admins see all approved requests.
    """
    try:
        # For managers, filter by their managed employees
        # For admin/superadmin, show all approved requests
        manager_id = current_user.employee_id if role == "manager" else None
        
        filters = ReimbursementSearchFiltersDTO(
            status="approved",
            approved_by=manager_id,
            page=offset // limit + 1,
            page_size=limit
        )
        
        result = await controller.list_reimbursement_requests(filters, current_user)
        return result.reimbursements
        
    except Exception as e:
        logger.error(f"Error getting approved reimbursement requests (legacy): {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/requests/{request_id}", response_model=ReimbursementResponseDTO)
async def get_reimbursement_request(
    request_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Get a specific reimbursement request by ID.
    
    - **request_id**: ID of the reimbursement request
    """
    try:
        result = await controller.get_reimbursement_request(request_id, current_user)
        return result
        
    except Exception as e:
        logger.error(f"Error getting reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/requests/{request_id}", response_model=ReimbursementResponseDTO)
async def update_reimbursement_request(
    request_id: str,
    request_data: ReimbursementRequestCreateDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Update a reimbursement request.
    
    - **request_id**: ID of the reimbursement request
    - **request_data**: Updated request data
    """
    try:
        # Convert to update DTO (only amount and description can be updated)
        update_data = ReimbursementRequestUpdateDTO(
            amount=request_data.amount,
            description=request_data.description
        )
        
        result = await controller.update_reimbursement_request(
            request_id, update_data, current_user
        )
        return result
        
    except Exception as e:
        logger.error(f"Error updating reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/requests/{request_id}/approve", response_model=ReimbursementResponseDTO)
async def approve_reimbursement_request(
    request_id: str,
    approval_data: ReimbursementApprovalDTO,
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Approve a reimbursement request.
    
    - **request_id**: ID of the reimbursement request
    - **approval_data**: Approval details and comments
    """
    try:
        result = await controller.approve_reimbursement_request(
            request_id, approval_data, current_user
        )
        return result
        
    except Exception as e:
        logger.error(f"Error approving reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/requests/{request_id}/reject", response_model=ReimbursementResponseDTO)
async def reject_reimbursement_request(
    request_id: str,
    comments: str = Body(..., embed=True),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["manager", "admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Reject a reimbursement request.
    
    - **request_id**: ID of the reimbursement request
    - **comments**: Reason for rejection
    """
    try:
        rejection_data = ReimbursementRejectionDTO(comments=comments)
        result = await controller.reject_reimbursement_request(
            request_id, rejection_data, current_user
        )
        return result
        
    except Exception as e:
        logger.error(f"Error rejecting reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/requests/{request_id}")
async def delete_reimbursement_request(
    request_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Delete a reimbursement request.
    
    - **request_id**: ID of the reimbursement request
    """
    try:
        result = await controller.delete_reimbursement_request(request_id, current_user)
        return result
        
    except Exception as e:
        logger.error(f"Error deleting reimbursement request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Reimbursement Type Endpoints

@router.post("/types", response_model=ReimbursementTypeResponseDTO)
async def create_reimbursement_type(
    type_data: ReimbursementTypeCreateRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Create a new reimbursement type.
    
    - **category_name**: Name of the reimbursement type
    - **description**: Optional description
    - **max_limit**: Optional maximum limit per request
    - **is_approval_required**: Whether approval is required
    - **is_receipt_required**: Whether receipt is required
    """
    try:
        result = await controller.create_reimbursement_type(type_data, current_user)
        logger.info(f"Reimbursement type created: {result}")
        return result
        
    except ReimbursementValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating reimbursement type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/types", response_model=List[ReimbursementTypeOptionsDTO])
async def get_reimbursement_types(
    active_only: bool = Query(True, description="Return only active types"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Get all reimbursement types.
    
    - **active_only**: Whether to return only active types
    """
    try:
        result = await controller.list_reimbursement_types(
            include_inactive=not active_only, 
            current_user=current_user
        )
        return result
        
    except Exception as e:
        logger.error(f"Error getting reimbursement types: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/types/{type_id}", response_model=ReimbursementTypeResponseDTO)
async def get_reimbursement_type(
    type_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Get a specific reimbursement type by ID.
    
    - **type_id**: ID of the reimbursement type
    """
    try:
        result = await controller.get_reimbursement_type(type_id, current_user)
        return result
        
    except Exception as e:
        logger.error(f"Error getting reimbursement type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/types/{type_id}", response_model=ReimbursementTypeResponseDTO)
async def update_reimbursement_type(
    type_id: str,
    type_data: ReimbursementTypeCreateRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Update a reimbursement type.
    
    - **type_id**: ID of the reimbursement type
    - **type_data**: Updated type data
    """
    try:
        # Convert to update DTO
        update_data = ReimbursementTypeUpdateRequestDTO(
            category_name=type_data.category_name,
            description=type_data.description,
            max_limit=type_data.max_limit
        )
        
        result = await controller.update_reimbursement_type(
            type_id, update_data, current_user
        )
        return result
        
    except Exception as e:
        logger.error(f"Error updating reimbursement type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/types/{type_id}")
async def delete_reimbursement_type(
    type_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Delete (deactivate) a reimbursement type.
    
    - **type_id**: ID of the reimbursement type
    """
    try:
        result = await controller.delete_reimbursement_type(type_id, current_user)
        return result
        
    except Exception as e:
        logger.error(f"Error deleting reimbursement type: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/debug/requests/{request_id}/check")
async def debug_check_request(
    request_id: str,
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Debug endpoint to check if a request exists (no auth required).
    """
    try:
        logger.info(f"DEBUG: Checking request existence for ID: {request_id}")
        
        # Use the existing service to trigger the debugging
        from app.config.dependency_container import get_dependency_container
        container = get_dependency_container()
        service = container.get_reimbursement_service()
        
        # Create a fake current user for localhost
        from app.auth.auth_dependencies import CurrentUser
        fake_payload = {
            "employee_id": "debug",
            "username": "debug",
            "hostname": "localhost",
            "role": "admin"
        }
        fake_user = CurrentUser(fake_payload)
        
        # This will trigger our enhanced debugging in the service
        try:
            result = await service.get_reimbursement_request_by_id(request_id, fake_user)
            logger.info(f"DEBUG: Service returned: {result is not None}")
        except Exception as e:
            logger.info(f"DEBUG: Service error: {e}")
        
        # Now get the collection directly for our own debugging
        repository = container.get_reimbursement_repository()
        collection = await repository._get_reimbursements_collection("localhost")
        
        # List ALL document IDs
        all_docs = await collection.find({}, {"request_id": 1, "reimbursement_id": 1, "_id": 1, "employee_id": 1, "status": 1, "receipt_file_name": 1}).to_list(length=None)
        logger.info(f"DEBUG: All document IDs in database:")
        for i, doc in enumerate(all_docs, 1):
            logger.info(f"  {i}. _id: {doc.get('_id')}")
            logger.info(f"     request_id: {doc.get('request_id')}")
            logger.info(f"     reimbursement_id: {doc.get('reimbursement_id')}")
            logger.info(f"     employee_id: {doc.get('employee_id')}")
            logger.info(f"     status: {doc.get('status')}")
            logger.info(f"     receipt_file_name: {doc.get('receipt_file_name')}")
        
        # Check if the specific ID exists
        by_request_id = await collection.find_one({"request_id": request_id})
        by_reimbursement_id = await collection.find_one({"reimbursement_id": request_id})
        by_id = await collection.find_one({"_id": request_id})
        
        logger.info(f"DEBUG: Found by request_id: {by_request_id is not None}")
        logger.info(f"DEBUG: Found by reimbursement_id: {by_reimbursement_id is not None}")
        logger.info(f"DEBUG: Found by _id: {by_id is not None}")
        
        return {
            "request_id": request_id,
            "found_by_request_id": by_request_id is not None,
            "found_by_reimbursement_id": by_reimbursement_id is not None,
            "found_by_id": by_id is not None,
            "total_documents": len(all_docs),
            "all_request_ids": [doc.get('request_id') for doc in all_docs],
            "all_reimbursement_ids": [doc.get('reimbursement_id') for doc in all_docs]
        }
        
    except Exception as e:
        logger.error(f"DEBUG: Error checking request: {str(e)}")
        return {"error": str(e)}

@router.get("/requests/{request_id}/receipt/download")
async def download_receipt(
    request_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """
    Download receipt for a reimbursement request.
    
    - **request_id**: ID of the reimbursement request
    """
    try:
        logger.info(f"Starting receipt download for request: {request_id}")
        
        # Get the reimbursement request to check if receipt exists
        reimbursement = await controller.get_reimbursement_request(request_id, current_user)
        logger.info(f"Reimbursement found. Receipt file name: {reimbursement.receipt_file_name}")
        
        if not reimbursement.receipt_file_name:
            logger.warning(f"No receipt file name found for request: {request_id}")
            raise HTTPException(status_code=404, detail="No receipt found for this reimbursement request")
        
        # Get the receipt file path from the reimbursement
        receipt_path = await controller.get_receipt_file_path(request_id, current_user)
        logger.info(f"Receipt file path retrieved: {receipt_path}")
        
        if not receipt_path:
            logger.warning(f"Receipt file path is None for request: {request_id}")
            raise HTTPException(status_code=404, detail="Receipt file not found")
        
        # Check if file actually exists on filesystem
        import os
        if not os.path.exists(receipt_path):
            logger.error(f"Receipt file does not exist on filesystem: {receipt_path}")
            raise HTTPException(status_code=404, detail="Receipt file not found on filesystem")
        
        logger.info(f"Serving file: {receipt_path} as {reimbursement.receipt_file_name}")
        
        # Return the file as a streaming response
        return FileResponse(
            path=receipt_path,
            filename=reimbursement.receipt_file_name,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading receipt for request {request_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 