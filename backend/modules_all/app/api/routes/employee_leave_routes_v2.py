"""
Employee Leave Routes V2
SOLID-compliant FastAPI routes for employee leave operations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging

from app.application.dto.employee_leave_dto import (
    EmployeeLeaveCreateRequestDTO,
    EmployeeLeaveUpdateRequestDTO,
    EmployeeLeaveApprovalRequestDTO,
    EmployeeLeaveSearchFiltersDTO,
    EmployeeLeaveResponseDTO,
    EmployeeLeaveBalanceDTO,
    EmployeeLeaveAnalyticsDTO,
    LWPCalculationDTO,
    EmployeeLeaveValidationError,
    EmployeeLeaveBusinessRuleError,
    EmployeeLeaveNotFoundError,
    InsufficientLeaveBalanceError
)
from app.api.controllers.employee_leave_controller import EmployeeLeaveController
from app.config.dependency_container import get_dependency_container
from app.auth.auth_dependencies import CurrentUser, get_current_user, require_role

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/employee-leave", tags=["Employee Leave V2"])

def get_employee_leave_controller() -> EmployeeLeaveController:
    """Get employee leave controller instance."""
    try:
        container = get_dependency_container()
        return container.get_employee_leave_controller()
    except Exception as e:
        logger.warning(f"Could not get employee leave controller from container: {e}")
        return EmployeeLeaveController()

# Exception handlers
def handle_employee_leave_exceptions(func):
    """Decorator to handle employee leave exceptions"""
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


# Employee Leave Application Routes

@router.get("/", response_model=List[EmployeeLeaveResponseDTO])
@handle_employee_leave_exceptions
async def get_all_employee_leaves(
    status: Optional[str] = Query(None, description="Filter by status"),
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    limit: Optional[int] = Query(100, description="Limit results"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Get all employee leaves with optional filters."""
    
    logger.info(f"Retrieving all employee leaves by: {current_user.employee_id}")
    
    # Authorization check and filter adjustment
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if user_role not in ["admin", "superadmin"]:
        if user_role == "manager":
            # Managers can view their team's leaves
            from app.application.dto.employee_leave_dto import EmployeeLeaveSearchFiltersDTO
            filters = EmployeeLeaveSearchFiltersDTO(
                status=status,
                manager_id=current_employee_id,
                limit=limit
            )
        else:
            # Regular employees can only view their own leaves
            employee_id = current_employee_id
            from app.application.dto.employee_leave_dto import EmployeeLeaveSearchFiltersDTO
            filters = EmployeeLeaveSearchFiltersDTO(
                status=status,
                employee_id=employee_id,
                limit=limit
            )
    else:
        # Admins can view all leaves
        from app.application.dto.employee_leave_dto import EmployeeLeaveSearchFiltersDTO
        filters = EmployeeLeaveSearchFiltersDTO(
            status=status,
            employee_id=employee_id,
            limit=limit
        )
    
    response = await controller.search_leaves(filters, current_user)
    
    return response

@router.post("/apply", response_model=EmployeeLeaveResponseDTO)
@handle_employee_leave_exceptions
async def apply_employee_leave(
    request: EmployeeLeaveCreateRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """
    Apply for employee leave.
    
    Business Rules:
    - Employee must be active
    - Leave type must be valid
    - Sufficient leave balance required
    - No overlapping leave applications
    - Working days calculated excluding weekends and holidays
    """
    
    logger.info(f"Employee leave application request from: {current_user.employee_id}")
    
    response = await controller.apply_leave(
        request, 
        current_user.employee_id, 
        current_user.hostname
    )
    
    return JSONResponse(
        status_code=201,
        content=response.dict()
    )


@router.put("/{leave_id}/approve", response_model=EmployeeLeaveResponseDTO)
@handle_employee_leave_exceptions
async def approve_employee_leave(
    request: EmployeeLeaveApprovalRequestDTO,
    leave_id: str = Path(..., description="Leave application ID"),
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("manager")),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """
    Approve or reject employee leave application.
    
    Business Rules:
    - Only managers/admins can approve leaves
    - Leave must be in pending status
    - Managers can only approve their team members' leaves
    - Rejection requires reason/comments
    """
    
    logger.info(f"Leave approval request for {leave_id} by: {current_user.employee_id}")
    
    approver_id = current_user.employee_id
    if not approver_id:
        raise HTTPException(status_code=400, detail="Approver ID not found in token")
    
    # Check if user has approval permissions
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["manager", "admin", "superadmin"]:
        raise HTTPException(
            status_code=403, 
            detail="Insufficient permissions to approve leaves"
        )
    
    response = await controller.approve_leave(leave_id, request, approver_id, current_user.hostname)
    
    return response


# Employee Leave Query Routes

@router.get("/{leave_id}", response_model=EmployeeLeaveResponseDTO)
@handle_employee_leave_exceptions
async def get_employee_leave_by_id(
    leave_id: str = Path(..., description="Leave application ID"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Get employee leave application by ID."""
    
    logger.info(f"Retrieving leave: {leave_id}")
    
    response = await controller.get_leave_by_id(leave_id)
    
    if not response:
        raise HTTPException(status_code=404, detail="Leave application not found")
    
    # Check if user can access this leave (basic authorization)
    user_role = getattr(current_user, 'role', '').lower()
    employee_id = current_user.employee_id
    
    if (user_role not in ["admin", "superadmin"] and 
        response.employee_id != employee_id):
        # Additional check for managers accessing their team members' leaves
        if user_role != "manager":
            raise HTTPException(status_code=403, detail="Access denied")
    
    return response


@router.get("/employee/{employee_id}", response_model=List[EmployeeLeaveResponseDTO])
@handle_employee_leave_exceptions
async def get_employee_leaves(
    employee_id: str = Path(..., description="Employee ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: Optional[int] = Query(50, description="Limit results"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Get employee leaves by employee ID."""
    
    logger.info(f"Retrieving leaves for employee: {employee_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if (user_role not in ["admin", "superadmin"] and 
        employee_id != current_employee_id):
        if user_role != "manager":
            raise HTTPException(status_code=403, detail="Access denied")
    
    response = await controller.get_employee_leaves(employee_id, status, limit)
    
    return response


@router.get("/manager/{manager_id}", response_model=List[EmployeeLeaveResponseDTO])
@handle_employee_leave_exceptions
async def get_manager_team_leaves(
    manager_id: str = Path(..., description="Manager ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: Optional[int] = Query(100, description="Limit results"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Get leaves for all employees under a manager."""
    
    logger.info(f"Retrieving team leaves for manager: {manager_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if (user_role not in ["admin", "superadmin"] and 
        manager_id != current_employee_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    response = await controller.get_manager_leaves(manager_id, status, limit)
    
    return response


@router.get("/pending/approvals", response_model=List[EmployeeLeaveResponseDTO])
@handle_employee_leave_exceptions
async def get_pending_approvals(
    manager_id: Optional[str] = Query(None, description="Filter by manager"),
    limit: Optional[int] = Query(50, description="Limit results"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Get pending leave approvals."""
    
    logger.info(f"Retrieving pending approvals")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["manager", "admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # For managers, filter by their ID
    if user_role == "manager":
        manager_id = current_user.employee_id
    
    response = await controller.get_pending_approvals(manager_id, limit)
    
    return response


@router.post("/search", response_model=List[EmployeeLeaveResponseDTO])
@handle_employee_leave_exceptions
async def search_employee_leaves(
    filters: EmployeeLeaveSearchFiltersDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Search employee leaves with filters."""
    
    logger.info(f"Searching employee leaves")
    
    # Authorization check and filter adjustment
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if user_role not in ["admin", "superadmin"]:
        if user_role == "manager":
            # Managers can search their team's leaves
            filters.manager_id = current_employee_id
        else:
            # Regular employees can only search their own leaves
            filters.employee_id = current_employee_id
    
    response = await controller.search_leaves(filters)
    
    return response


@router.get("/employee/{employee_id}/monthly/{year}/{month}", 
           response_model=List[EmployeeLeaveResponseDTO])
@handle_employee_leave_exceptions
async def get_monthly_employee_leaves(
    employee_id: str = Path(..., description="Employee ID"),
    year: int = Path(..., description="Year"),
    month: int = Path(..., description="Month (1-12)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Get employee leaves for a specific month."""
    
    logger.info(f"Retrieving monthly leaves for {employee_id}: {month}/{year}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if (user_role not in ["admin", "superadmin"] and 
        employee_id != current_employee_id):
        if user_role != "manager":
            raise HTTPException(status_code=403, detail="Access denied")
    
    response = await controller.get_monthly_leaves(employee_id, month, year)
    
    return response


# Leave Balance and Analytics Routes

@router.get("/employee/{employee_id}/balance", response_model=EmployeeLeaveBalanceDTO)
@handle_employee_leave_exceptions
async def get_employee_leave_balance(
    employee_id: str = Path(..., description="Employee ID"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Get leave balance for an employee."""
    
    logger.info(f"Retrieving leave balance for: {employee_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if (user_role not in ["admin", "superadmin"] and 
        employee_id != current_employee_id):
        if user_role != "manager":
            raise HTTPException(status_code=403, detail="Access denied")
    
    response = await controller.get_leave_balance(employee_id)
    
    return response


@router.get("/analytics", response_model=EmployeeLeaveAnalyticsDTO)
@handle_employee_leave_exceptions
async def get_leave_analytics(
    employee_id: Optional[str] = Query(None, description="Filter by employee"),
    manager_id: Optional[str] = Query(None, description="Filter by manager"),
    year: Optional[int] = Query(None, description="Filter by year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Get leave analytics and statistics."""
    
    logger.info(f"Retrieving leave analytics")
    
    # Authorization check and filter adjustment
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if user_role not in ["admin", "superadmin"]:
        if user_role == "manager":
            # Managers can view their team analytics
            manager_id = current_employee_id
            employee_id = None  # Clear employee filter for team view
        else:
            # Regular employees can only view their own analytics
            employee_id = current_employee_id
            manager_id = None
    
    response = await controller.get_leave_analytics(employee_id, manager_id, year)
    
    return response


@router.get("/employee/{employee_id}/lwp/{year}/{month}", response_model=LWPCalculationDTO)
@handle_employee_leave_exceptions
async def calculate_employee_lwp(
    employee_id: str = Path(..., description="Employee ID"),
    year: int = Path(..., description="Year"),
    month: int = Path(..., description="Month (1-12)"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Calculate Leave Without Pay (LWP) for an employee for a specific month."""
    
    logger.info(f"Calculating LWP for {employee_id}: {month}/{year}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["admin", "superadmin", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    response = await controller.calculate_lwp(employee_id, month, year)
    
    return response


@router.get("/manager/{manager_id}/team-summary", response_model=List[Dict[str, Any]])
@handle_employee_leave_exceptions
async def get_team_leave_summary(
    manager_id: str = Path(..., description="Manager ID"),
    month: Optional[int] = Query(None, description="Filter by month"),
    year: Optional[int] = Query(None, description="Filter by year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Get team leave summary for a manager."""
    
    logger.info(f"Retrieving team summary for manager: {manager_id}")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if (user_role not in ["admin", "superadmin"] and 
        manager_id != current_employee_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    response = await controller.get_team_summary(manager_id, month, year)
    
    return response


@router.post("/count", response_model=int)
@handle_employee_leave_exceptions
async def count_employee_leaves(
    filters: EmployeeLeaveSearchFiltersDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """Count employee leaves matching filters."""
    
    logger.info(f"Counting employee leaves")
    
    # Authorization check and filter adjustment
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if user_role not in ["admin", "superadmin"]:
        if user_role == "manager":
            # Managers can count their team's leaves
            filters.manager_id = current_employee_id
        else:
            # Regular employees can only count their own leaves
            filters.employee_id = current_employee_id
    
    count = await controller.count_leaves(filters)
    
    return count


# Health check endpoint (public)
@router.get("/health")
async def health_check():
    """Health check endpoint for employee leave service."""
    return {
        "status": "healthy",
        "service": "employee-leave-v2",
        "version": "2.0.0"
    }


# Add these new legacy endpoints after the existing endpoints

@router.get("/user/{employee_id}/{month}/{year}", response_model=List[Dict[str, Any]])
@handle_employee_leave_exceptions
async def get_user_leaves_by_month_legacy(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2000, le=3000, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """
    Get user leaves for a specific month (Legacy endpoint for frontend compatibility).
    
    This endpoint provides backward compatibility for the frontend while maintaining
    the same business logic as the V2 API.
    """
    logger.info(f"Getting leaves for employee {employee_id} for {month}/{year} (legacy endpoint)")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    current_employee_id = current_user.employee_id
    
    if (user_role not in ["admin", "superadmin"] and 
        employee_id != current_employee_id):
        if user_role != "manager":
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Use the existing monthly leaves method
    v2_response = await controller.get_monthly_leaves(employee_id, month, year)
    
    # Transform to legacy format
    legacy_response = []
    for leave in v2_response:
        legacy_response.append({
            "leave_name": leave.leave_type,
            "status": leave.status,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "leave_count": leave.leave_count if hasattr(leave, 'leave_count') else 1,
            "days_in_month": leave.leave_count if hasattr(leave, 'leave_count') else 1,
            "reason": leave.reason if hasattr(leave, 'reason') else ""
        })
    
    return legacy_response


@router.get("/lwp/{employee_id}/{month}/{year}", response_model=Dict[str, Any])
@handle_employee_leave_exceptions
async def get_user_lwp_legacy(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2000, le=3000, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: EmployeeLeaveController = Depends(get_employee_leave_controller)
):
    """
    Get user LWP data for a specific month (Legacy endpoint for frontend compatibility).
    
    This endpoint provides backward compatibility for the frontend while maintaining
    the same business logic as the V2 API.
    """
    logger.info(f"Getting LWP for employee {employee_id} for {month}/{year} (legacy endpoint)")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["admin", "superadmin", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Use the existing LWP calculation method
    lwp_response = await controller.calculate_lwp(employee_id, month, year)
    
    # Transform to match frontend expectation
    return {
        "lwp_days": lwp_response.lwp_days if hasattr(lwp_response, 'lwp_days') else 0
    } 