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

# Only keep the legacy LWP endpoint used by the frontend
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
    """
    logger.info(f"Getting LWP for employee {employee_id} for {month}/{year} (legacy endpoint)")
    
    # Authorization check
    user_role = getattr(current_user, 'role', '').lower()
    if user_role not in ["admin", "superadmin", "manager"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Use the existing LWP calculation method
    lwp_response = await controller.calculate_lwp(employee_id, month, year, current_user)
    
    # Transform to match frontend expectation
    return {
        "lwp_days": lwp_response.lwp_days if hasattr(lwp_response, 'lwp_days') else 0
    } 