"""
Reimbursement API Controllers
FastAPI controllers for reimbursement management
"""

import logging
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Depends, Query, Path, UploadFile, File
from fastapi.responses import JSONResponse

from application.use_cases.reimbursement.create_reimbursement_type_use_case import CreateReimbursementTypeUseCase
from application.use_cases.reimbursement.create_reimbursement_request_use_case import CreateReimbursementRequestUseCase
from application.use_cases.reimbursement.approve_reimbursement_request_use_case import ApproveReimbursementRequestUseCase
from application.use_cases.reimbursement.get_reimbursement_requests_use_case import GetReimbursementRequestsUseCase
from application.use_cases.reimbursement.process_reimbursement_payment_use_case import ProcessReimbursementPaymentUseCase
from application.dto.reimbursement_dto import (
    ReimbursementTypeCreateRequestDTO,
    ReimbursementTypeUpdateRequestDTO,
    ReimbursementTypeResponseDTO,
    ReimbursementRequestCreateDTO,
    ReimbursementRequestUpdateDTO,
    ReimbursementResponseDTO,
    ReimbursementApprovalDTO,
    ReimbursementPaymentDTO,
    ReimbursementSearchFiltersDTO,
    ReimbursementStatisticsDTO,
    ReimbursementValidationError,
    ReimbursementBusinessRuleError
)
from auth.dependencies import get_current_user


logger = logging.getLogger(__name__)

# Create router
reimbursement_router = APIRouter(prefix="/api/reimbursements", tags=["reimbursements"])


class ReimbursementController:
    """
    Controller for reimbursement management operations.
    
    Follows SOLID principles:
    - SRP: Each endpoint handles a single operation
    - OCP: Extensible through dependency injection
    - LSP: Can be substituted with enhanced versions
    - ISP: Focused on reimbursement operations
    - DIP: Depends on use case abstractions
    """
    
    def __init__(
        self,
        create_type_use_case: CreateReimbursementTypeUseCase,
        create_request_use_case: CreateReimbursementRequestUseCase,
        approve_request_use_case: ApproveReimbursementRequestUseCase,
        get_requests_use_case: GetReimbursementRequestsUseCase,
        process_payment_use_case: ProcessReimbursementPaymentUseCase
    ):
        self.create_type_use_case = create_type_use_case
        self.create_request_use_case = create_request_use_case
        self.approve_request_use_case = approve_request_use_case
        self.get_requests_use_case = get_requests_use_case
        self.process_payment_use_case = process_payment_use_case


# Global controller instance (will be injected)
controller: Optional[ReimbursementController] = None


def get_reimbursement_controller() -> ReimbursementController:
    """Dependency injection for reimbursement controller"""
    if controller is None:
        raise HTTPException(status_code=500, detail="Reimbursement controller not initialized")
    return controller


# ==================== REIMBURSEMENT TYPE ENDPOINTS ====================

@reimbursement_router.post("/types", response_model=ReimbursementTypeResponseDTO)
async def create_reimbursement_type(
    request: ReimbursementTypeCreateRequestDTO,
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Create a new reimbursement type"""
    try:
        logger.info(f"Creating reimbursement type: {request.code} by {current_user.get('employee_id')}")
        
        response = await controller.create_type_use_case.execute(
            request=request,
            created_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except ReimbursementValidationError as e:
        logger.warning(f"Validation error creating reimbursement type: {e}")
        raise HTTPException(status_code=400, detail={"error": e.error_code, "message": str(e)})
    
    except ReimbursementBusinessRuleError as e:
        logger.warning(f"Business rule error creating reimbursement type: {e}")
        raise HTTPException(status_code=422, detail={"error": e.error_code, "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error creating reimbursement type: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@reimbursement_router.get("/types", response_model=List[ReimbursementTypeResponseDTO])
async def get_reimbursement_types(
    active_only: bool = Query(True, description="Return only active types"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Get all reimbursement types"""
    try:
        logger.info(f"Getting reimbursement types (active_only: {active_only}, category: {category})")
        
        # This would need to be implemented in the use case
        # For now, return empty list
        return []
        
    except Exception as e:
        logger.error(f"Error getting reimbursement types: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@reimbursement_router.get("/types/{type_id}", response_model=ReimbursementTypeResponseDTO)
async def get_reimbursement_type(
    type_id: str = Path(..., description="Reimbursement type ID"),
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Get reimbursement type by ID"""
    try:
        logger.info(f"Getting reimbursement type: {type_id}")
        
        # This would need to be implemented in the use case
        # For now, raise not found
        raise HTTPException(status_code=404, detail="Reimbursement type not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reimbursement type {type_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== REIMBURSEMENT REQUEST ENDPOINTS ====================

@reimbursement_router.post("/requests", response_model=ReimbursementResponseDTO)
async def create_reimbursement_request(
    request: ReimbursementRequestCreateDTO,
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Create a new reimbursement request"""
    try:
        logger.info(f"Creating reimbursement request for employee: {request.employee_id}")
        
        response = await controller.create_request_use_case.execute(
            request=request,
            created_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except ReimbursementValidationError as e:
        logger.warning(f"Validation error creating reimbursement request: {e}")
        raise HTTPException(status_code=400, detail={"error": e.error_code, "message": str(e)})
    
    except ReimbursementBusinessRuleError as e:
        logger.warning(f"Business rule error creating reimbursement request: {e}")
        raise HTTPException(status_code=422, detail={"error": e.error_code, "message": str(e)})
    
    except Exception as e:
        logger.error(f"Unexpected error creating reimbursement request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@reimbursement_router.get("/requests", response_model=List[ReimbursementResponseDTO])
async def get_reimbursement_requests(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: Optional[int] = Query(100, description="Maximum number of results"),
    include_drafts: bool = Query(False, description="Include draft requests"),
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Get reimbursement requests with optional filters"""
    try:
        logger.info(f"Getting reimbursement requests with filters")
        
        # If employee_id is provided, get requests for that employee
        if employee_id:
            return await controller.get_requests_use_case.get_requests_by_employee(employee_id)
        
        # If status is provided, get requests by status
        if status:
            return await controller.get_requests_use_case.get_requests_by_status(status)
        
        # If date range is provided, get requests by date range
        if start_date and end_date:
            return await controller.get_requests_use_case.get_requests_by_date_range(start_date, end_date)
        
        # Otherwise, get all requests
        return await controller.get_requests_use_case.get_all_requests(include_drafts)
        
    except Exception as e:
        logger.error(f"Error getting reimbursement requests: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@reimbursement_router.get("/requests/{request_id}", response_model=ReimbursementResponseDTO)
async def get_reimbursement_request(
    request_id: str = Path(..., description="Reimbursement request ID"),
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Get reimbursement request by ID"""
    try:
        logger.info(f"Getting reimbursement request: {request_id}")
        
        response = await controller.get_requests_use_case.get_request_by_id(request_id)
        
        if not response:
            raise HTTPException(status_code=404, detail="Reimbursement request not found")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reimbursement request {request_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@reimbursement_router.get("/requests/employee/{employee_id}", response_model=List[ReimbursementResponseDTO])
async def get_employee_reimbursement_requests(
    employee_id: str = Path(..., description="Employee ID"),
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Get reimbursement requests for a specific employee"""
    try:
        logger.info(f"Getting reimbursement requests for employee: {employee_id}")
        
        # Check if user can access this employee's data
        if current_user.get("employee_id") != employee_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return await controller.get_requests_use_case.get_requests_by_employee(employee_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employee reimbursement requests: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@reimbursement_router.get("/requests/pending-approval", response_model=List[ReimbursementResponseDTO])
async def get_pending_approval_requests(
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Get reimbursement requests pending approval"""
    try:
        logger.info("Getting reimbursement requests pending approval")
        
        # Check if user has approval permissions
        if not current_user.get("can_approve_reimbursements", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return await controller.get_requests_use_case.get_pending_approval_requests()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pending approval requests: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== REIMBURSEMENT APPROVAL ENDPOINTS ====================

@reimbursement_router.post("/requests/{request_id}/approve", response_model=ReimbursementResponseDTO)
async def approve_reimbursement_request(
    request_id: str = Path(..., description="Reimbursement request ID"),
    approval_request: ReimbursementApprovalDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Approve a reimbursement request"""
    try:
        logger.info(f"Approving reimbursement request: {request_id}")
        
        # Check if user has approval permissions
        if not current_user.get("can_approve_reimbursements", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Use default approval if none provided
        if approval_request is None:
            approval_request = ReimbursementApprovalDTO(
                approval_level=current_user.get("approval_level", "manager"),
                comments="Approved"
            )
        
        response = await controller.approve_request_use_case.execute(
            request_id=request_id,
            approval_request=approval_request,
            approved_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except ReimbursementValidationError as e:
        logger.warning(f"Validation error approving reimbursement request: {e}")
        raise HTTPException(status_code=400, detail={"error": e.error_code, "message": str(e)})
    
    except ReimbursementBusinessRuleError as e:
        logger.warning(f"Business rule error approving reimbursement request: {e}")
        raise HTTPException(status_code=422, detail={"error": e.error_code, "message": str(e)})
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error approving reimbursement request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@reimbursement_router.post("/requests/{request_id}/reject", response_model=ReimbursementResponseDTO)
async def reject_reimbursement_request(
    request_id: str = Path(..., description="Reimbursement request ID"),
    rejection_reason: str = Query(..., description="Reason for rejection"),
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Reject a reimbursement request"""
    try:
        logger.info(f"Rejecting reimbursement request: {request_id}")
        
        # Check if user has approval permissions
        if not current_user.get("can_approve_reimbursements", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # This would need to be implemented with a reject use case
        # For now, return not implemented
        raise HTTPException(status_code=501, detail="Reject functionality not implemented yet")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting reimbursement request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== REIMBURSEMENT PAYMENT ENDPOINTS ====================

@reimbursement_router.post("/requests/{request_id}/process-payment", response_model=ReimbursementResponseDTO)
async def process_reimbursement_payment(
    request_id: str = Path(..., description="Reimbursement request ID"),
    payment_request: ReimbursementPaymentDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Process payment for a reimbursement request"""
    try:
        logger.info(f"Processing payment for reimbursement request: {request_id}")
        
        # Check if user has payment processing permissions
        if not current_user.get("can_process_payments", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Use default payment method if none provided
        if payment_request is None:
            payment_request = ReimbursementPaymentDTO(
                payment_method="bank_transfer",
                payment_reference=f"PAY-{request_id}-{datetime.now().strftime('%Y%m%d')}"
            )
        
        response = await controller.process_payment_use_case.execute(
            request_id=request_id,
            payment_request=payment_request,
            processed_by=current_user.get("employee_id", "unknown")
        )
        
        return response
        
    except ReimbursementValidationError as e:
        logger.warning(f"Validation error processing payment: {e}")
        raise HTTPException(status_code=400, detail={"error": e.error_code, "message": str(e)})
    
    except ReimbursementBusinessRuleError as e:
        logger.warning(f"Business rule error processing payment: {e}")
        raise HTTPException(status_code=422, detail={"error": e.error_code, "message": str(e)})
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing payment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== REIMBURSEMENT ANALYTICS ENDPOINTS ====================

@reimbursement_router.get("/analytics/statistics", response_model=ReimbursementStatisticsDTO)
async def get_reimbursement_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Get reimbursement statistics"""
    try:
        logger.info("Getting reimbursement statistics")
        
        # Check if user has analytics permissions
        if not current_user.get("can_view_analytics", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return await controller.get_requests_use_case.get_reimbursement_statistics(start_date, end_date)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reimbursement statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@reimbursement_router.get("/analytics/employee/{employee_id}/statistics")
async def get_employee_reimbursement_statistics(
    employee_id: str = Path(..., description="Employee ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Get reimbursement statistics for a specific employee"""
    try:
        logger.info(f"Getting reimbursement statistics for employee: {employee_id}")
        
        # Check if user can access this employee's data
        if current_user.get("employee_id") != employee_id and not current_user.get("can_view_analytics", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return await controller.get_requests_use_case.get_employee_statistics(employee_id, start_date, end_date)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting employee statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== UTILITY ENDPOINTS ====================

@reimbursement_router.post("/requests/{request_id}/upload-receipt")
async def upload_receipt(
    request_id: str = Path(..., description="Reimbursement request ID"),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    controller: ReimbursementController = Depends(get_reimbursement_controller)
):
    """Upload receipt for a reimbursement request"""
    try:
        logger.info(f"Uploading receipt for reimbursement request: {request_id}")
        
        # This would need to be implemented with file handling logic
        # For now, return not implemented
        raise HTTPException(status_code=501, detail="Receipt upload functionality not implemented yet")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading receipt: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@reimbursement_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "reimbursement"}


# ==================== CONTROLLER INITIALIZATION ====================

def initialize_reimbursement_controller(
    create_type_use_case: CreateReimbursementTypeUseCase,
    create_request_use_case: CreateReimbursementRequestUseCase,
    approve_request_use_case: ApproveReimbursementRequestUseCase,
    get_requests_use_case: GetReimbursementRequestsUseCase,
    process_payment_use_case: ProcessReimbursementPaymentUseCase
):
    """Initialize the global reimbursement controller"""
    global controller
    controller = ReimbursementController(
        create_type_use_case=create_type_use_case,
        create_request_use_case=create_request_use_case,
        approve_request_use_case=approve_request_use_case,
        get_requests_use_case=get_requests_use_case,
        process_payment_use_case=process_payment_use_case
    )
    logger.info("Reimbursement controller initialized successfully") 