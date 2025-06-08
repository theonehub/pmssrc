"""
Leaves API Routes V2
SOLID-compliant FastAPI routes for leave operations following the User Module Architecture Guide
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from datetime import datetime

from app.api.controllers.employee_leave_controller import EmployeeLeaveController
from app.application.dto.employee_leave_dto import (
    EmployeeLeaveCreateRequestDTO,
    EmployeeLeaveUpdateRequestDTO,
    EmployeeLeaveApprovalRequestDTO,
    EmployeeLeaveSearchFiltersDTO,
    EmployeeLeaveResponseDTO,
    EmployeeLeaveBalanceDTO,
    EmployeeLeaveAnalyticsDTO,
    EmployeeLeaveValidationError,
    EmployeeLeaveBusinessRuleError,
    EmployeeLeaveNotFoundError,
    InsufficientLeaveBalanceError
)
from app.auth.auth_dependencies import CurrentUser, get_current_user, require_role
from app.config.dependency_container import get_dependency_container

logger = logging.getLogger(__name__)

# Create router following architecture guide
router = APIRouter(prefix="/api/v2/leaves", tags=["leaves-v2"])

def get_employee_leave_controller() -> EmployeeLeaveController:
    """Get employee leave controller instance following DI pattern."""
    try:
        container = get_dependency_container()
        return container.get_employee_leave_controller()
    except Exception as e:
        logger.warning(f"Could not get employee leave controller from container: {e}")
        return EmployeeLeaveController()

# Exception handler decorator following architecture guide
def handle_leave_exceptions(func):
    """Decorator to handle leave exceptions following SOLID principles"""
    from functools import wraps
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except EmployeeLeaveValidationError as e:
            logger.warning(f"Validation error: {e.errors}")
            raise HTTPException(status_code=400, detail={
                "error": "Validation Error",
                "message": "Request validation failed",
                "details": e.errors
            })
        except EmployeeLeaveBusinessRuleError as e:
            logger.warning(f"Business rule violation: {e.message}")
            raise HTTPException(status_code=422, detail={
                "error": "Business Rule Violation",
                "message": e.message
            })
        except InsufficientLeaveBalanceError as e:
            logger.warning(f"Insufficient leave balance: {e.message}")
            raise HTTPException(status_code=422, detail={
                "error": "Insufficient Leave Balance",
                "message": e.message,
                "details": {
                    "leave_type": e.leave_type,
                    "required": e.required,
                    "available": e.available
                }
            })
        except EmployeeLeaveNotFoundError as e:
            logger.warning(f"Leave not found: {e.leave_id}")
            raise HTTPException(status_code=404, detail={
                "error": "Leave Not Found",
                "message": f"Leave application not found: {e.leave_id}"
            })
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred"
            })
    return wrapper

# Health check endpoint following architecture guide
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check for leaves service following architecture guide."""
    return {
        "status": "healthy", 
        "service": "leaves-v2",
        "version": "2.0.0"
    }

# Frontend-compatible endpoints following architecture guide

@router.post("/apply", response_model=EmployeeLeaveResponseDTO)
@handle_leave_exceptions
async def apply_for_leave(
    request: Dict[str, Any] = Body(...),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
) -> EmployeeLeaveResponseDTO:
    """Apply for leave - Frontend compatible endpoint."""
    logger.info(f"Leave application request from: {current_user.employee_id} in org: {current_user.hostname}")
    
    # Transform frontend request to backend DTO
    backend_request = EmployeeLeaveCreateRequestDTO(
        leave_name=request.get('leave_name', ''),
        start_date=request.get('start_date', ''),
        end_date=request.get('end_date', ''),
        reason=request.get('reason', ''),
        employee_id=current_user.employee_id
    )
    
    response = await controller.apply_leave(
        backend_request, 
        current_user
    )
    
    return JSONResponse(
        status_code=201,
        content=response.dict()
    )

@router.get("/my-leaves", response_model=List[Dict[str, Any]])
@handle_leave_exceptions
async def get_my_leaves(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: Optional[int] = Query(50, description="Limit results"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
) -> List[Dict[str, Any]]:
    """Get current user's leaves - Frontend compatible endpoint."""
    logger.info(f"Retrieving leaves for current user: {current_user.employee_id}")
    
    response = await controller.get_employee_leaves(
        current_user.employee_id, 
        status, 
        limit,
        current_user
    )
    
    # Transform to frontend format
    frontend_response = []
    for leave in response:
        frontend_leave = {
            "id": leave.leave_id if hasattr(leave, 'leave_id') else leave.id,
            "_id": leave.leave_id if hasattr(leave, 'leave_id') else leave.id,
            "leave_name": leave.leave_type if hasattr(leave, 'leave_type') else leave.leave_name,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "leave_count": leave.days_requested if hasattr(leave, 'days_requested') else leave.leave_count,
            "reason": leave.reason,
            "status": leave.status
        }
        frontend_response.append(frontend_leave)
    
    return frontend_response

@router.get("/leave-balance", response_model=Dict[str, Any])
@handle_leave_exceptions
async def get_leave_balance(
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
) -> Dict[str, Any]:
    """Get leave balance for current user - Frontend compatible endpoint."""
    logger.info(f"Retrieving leave balance for: {current_user.employee_id}")
    
    response = await controller.get_leave_balance(current_user.employee_id, current_user)
    
    # Transform to frontend format (key-value pairs of leave type and balance)
    if hasattr(response, 'balances') and response.balances:
        return response.balances
    else:
        # Default leave types if no balance data
        return {
            "casual_leave": 12,
            "sick_leave": 12,
            "earned_leave": 21,
            "maternity_leave": 180,
            "paternity_leave": 15
        }

@router.get("/all", response_model=List[Dict[str, Any]])
@handle_leave_exceptions
async def get_all_leaves(
    status: Optional[str] = Query(None, description="Filter by status"),
    employee_name: Optional[str] = Query(None, description="Filter by employee name"),
    limit: Optional[int] = Query(100, description="Limit results"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
) -> List[Dict[str, Any]]:
    """Get all leaves - Frontend compatible endpoint for managers/admins."""
    logger.info(f"Retrieving all leaves by: {current_user.employee_id}")
    
    # Authorization check following architecture guide
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["manager", "admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create search filters
    filters = EmployeeLeaveSearchFiltersDTO(
        status=status,
        employee_name=employee_name,
        limit=limit,
        manager_id=current_user.employee_id
    )
    
    response = await controller.search_leaves(filters, current_user)
    
    # Transform response to frontend format
    frontend_response = []
    for leave in response:
        frontend_leave = {
            "id": leave.leave_id if hasattr(leave, 'leave_id') else leave.id,
            "leave_id": leave.leave_id if hasattr(leave, 'leave_id') else leave.id,
            "employee_id": leave.employee_id,
            "emp_name": leave.employee_name if hasattr(leave, 'employee_name') else "Unknown",
            "emp_email": leave.employee_email if hasattr(leave, 'employee_email') else "unknown@example.com",
            "employee_name": leave.employee_name if hasattr(leave, 'employee_name') else "Unknown",
            "employee_email": leave.employee_email if hasattr(leave, 'employee_email') else "unknown@example.com",
            "leave_name": leave.leave_type if hasattr(leave, 'leave_type') else leave.leave_name,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "leave_count": leave.days_requested if hasattr(leave, 'days_requested') else leave.leave_count,
            "status": leave.status
        }
        frontend_response.append(frontend_leave)
    
    return frontend_response

@router.get("/stats", response_model=Dict[str, Any])
@handle_leave_exceptions
async def get_leave_stats(
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
) -> Dict[str, Any]:
    """Get leave statistics - Frontend compatible endpoint."""
    logger.info(f"Retrieving leave statistics by: {current_user.employee_id}")
    
    # Authorization check following architecture guide
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["manager", "admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get analytics data
    analytics = await controller.get_leave_analytics(
        employee_id=None,
        manager_id=current_user.employee_id,
        year=None,
        current_user=current_user
    )
    
    # Transform to frontend-expected format
    stats = {
        "total": analytics.total_applications if hasattr(analytics, 'total_applications') else 0,
        "pending": analytics.pending_applications if hasattr(analytics, 'pending_applications') else 0,
        "approved": analytics.approved_applications if hasattr(analytics, 'approved_applications') else 0,
        "rejected": analytics.rejected_applications if hasattr(analytics, 'rejected_applications') else 0
    }
    
    return stats

@router.put("/{leave_id}/status", response_model=Dict[str, Any])
@handle_leave_exceptions
async def update_leave_status(
    leave_id: str = Path(..., description="Leave application ID"),
    status: str = Query(..., description="New status (approved/rejected)"),
    comments: Optional[str] = Query(None, description="Approval/rejection comments"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
) -> Dict[str, Any]:
    """Update leave status - Frontend compatible endpoint."""
    logger.info(f"Leave status update for {leave_id} by: {current_user.employee_id}")
    
    # Authorization check following architecture guide
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["manager", "admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions to approve leaves")
    
    # Create approval request
    approval_request = EmployeeLeaveApprovalRequestDTO(
        status=status,
        comments=comments,
        approved_by=current_user.employee_id
    )
    
    response = await controller.approve_leave(
        leave_id, 
        approval_request, 
        current_user
    )
    
    return {"message": f"Leave {status} successfully", "leave": response.dict()}

@router.put("/{leave_id}", response_model=Dict[str, Any])
@handle_leave_exceptions
async def update_leave(
    leave_id: str = Path(..., description="Leave application ID"),
    request: Dict[str, Any] = Body(...),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
) -> Dict[str, Any]:
    """Update leave application - Frontend compatible endpoint."""
    logger.info(f"Leave update for {leave_id} by: {current_user.employee_id}")
    
    # Get existing leave to check ownership
    existing_leave = await controller.get_leave_by_id(leave_id, current_user)
    if not existing_leave:
        raise HTTPException(status_code=404, detail="Leave application not found")
    
    # Authorization check - only owner or admin can update
    user_role = getattr(current_user, 'role', '').lower()
    if (user_role not in ["admin", "superadmin"] and 
        existing_leave.employee_id != current_user.employee_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Transform frontend request to backend DTO
    update_request = EmployeeLeaveUpdateRequestDTO(
        leave_name=request.get('leave_name'),
        start_date=request.get('start_date'),
        end_date=request.get('end_date'),
        reason=request.get('reason'),
        updated_by=current_user.employee_id
    )
    
    response = await controller.update_leave(leave_id, update_request, current_user)
    
    return {"message": "Leave updated successfully", "leave": response.dict()}

# Additional endpoints for comprehensive leave management

@router.get("/pending", response_model=List[EmployeeLeaveResponseDTO])
@handle_leave_exceptions
async def get_pending_leaves(
    limit: Optional[int] = Query(50, description="Limit results"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
) -> List[EmployeeLeaveResponseDTO]:
    """
    Get pending leaves for approval - Following architecture guide.
    """
    logger.info(f"Retrieving pending leaves for: {current_user.employee_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["manager", "admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    manager_id = current_user.employee_id if user_role == "manager" else None
    
    response = await controller.get_pending_approvals(manager_id, limit, current_user)
    
    return response

@router.post("/search", response_model=List[EmployeeLeaveResponseDTO])
@handle_leave_exceptions
async def search_leaves(
    filters: EmployeeLeaveSearchFiltersDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
) -> List[EmployeeLeaveResponseDTO]:
    """
    Search leaves with filters - Following architecture guide.
    """
    logger.info(f"Searching leaves by: {current_user.employee_id}")
    
    # Authorization and filter adjustment following architecture guide
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if user_role not in ["admin", "superadmin"]:
        if user_role == "manager":
            filters.manager_id = current_employee_id
        else:
            filters.employee_id = current_employee_id
    
    response = await controller.search_leaves(filters, current_user)
    
    return response 