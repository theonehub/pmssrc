"""
Monthly Payout Routes v2
FastAPI routes for monthly payout operations with LWP integration
"""

from fastapi import APIRouter, Depends, Query, Path
from typing import List, Optional, Dict, Any

from app.api.controllers.monthly_payout_controller import MonthlyPayoutController
from app.application.dto.payroll_dto import (
    MonthlyPayoutRequestDTO,
    MonthlyPayoutResponseDTO,
    BulkPayoutRequestDTO,
    PayoutUpdateDTO,
    PayoutApprovalDTO,
    PayoutProcessingDTO,
    PayslipDataDTO
)
from app.auth.auth_dependencies import get_current_user, CurrentUser

# Initialize router
router = APIRouter(prefix="/api/v2/monthly-payouts", tags=["Monthly Payouts"])

# Import the dependency function from the container
from app.config.dependency_container import get_monthly_payout_controller


@router.post(
    "/compute",
    response_model=MonthlyPayoutResponseDTO,
    summary="Compute Monthly Payout",
    description="Compute monthly payout for a single employee with LWP adjustments"
)
async def compute_employee_monthly_payout(
    request: MonthlyPayoutRequestDTO,
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> MonthlyPayoutResponseDTO:
    """Compute monthly payout for a single employee."""
    return await controller.compute_employee_monthly_payout(request, current_user)


@router.post(
    "/compute/bulk",
    response_model=Dict[str, Any],
    summary="Bulk Compute Monthly Payouts",
    description="Compute monthly payouts for multiple employees"
)
async def compute_bulk_monthly_payouts(
    request: BulkPayoutRequestDTO,
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """Compute monthly payouts for multiple employees."""
    return await controller.compute_bulk_monthly_payouts(request, current_user)


@router.get(
    "/employee/{employee_id}",
    response_model=MonthlyPayoutResponseDTO,
    summary="Get Employee Monthly Payout",
    description="Get existing monthly payout for a specific employee"
)
async def get_employee_monthly_payout(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2050, description="Year"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> MonthlyPayoutResponseDTO:
    """Get existing monthly payout for a specific employee."""
    return await controller.get_employee_monthly_payout(
        employee_id, month, year, current_user
    )


@router.get(
    "/summary",
    response_model=Dict[str, Any],
    summary="Get Monthly Payouts Summary",
    description="Get summary of all monthly payouts for a given period"
)
async def get_monthly_payouts_summary(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2050, description="Year"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get summary of all monthly payouts for a given period."""
    return await controller.get_monthly_payouts_summary(month, year, current_user)


@router.get(
    "/search",
    response_model=Dict[str, Any],
    summary="Search Monthly Payouts",
    description="Search monthly payouts with filters and pagination"
)
async def search_monthly_payouts(
    employee_id: Optional[str] = Query(None, description="Employee ID filter"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Month filter"),
    year: Optional[int] = Query(None, ge=2020, le=2050, description="Year filter"),
    status: Optional[str] = Query(None, description="Status filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Page size"),
    sort_by: Optional[str] = Query("calculation_date", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """Search monthly payouts with filters and pagination."""
    return await controller.search_monthly_payouts(
        employee_id, month, year, status, page, page_size, sort_by, sort_order, current_user
    )


@router.put(
    "/employee/{employee_id}",
    response_model=MonthlyPayoutResponseDTO,
    summary="Update Monthly Payout",
    description="Update monthly payout details"
)
async def update_monthly_payout(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2050, description="Year"),
    update_data: PayoutUpdateDTO = ...,
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> MonthlyPayoutResponseDTO:
    """Update monthly payout details."""
    return await controller.update_monthly_payout(
        employee_id, month, year, update_data, current_user
    )


@router.post(
    "/employee/{employee_id}/approve",
    response_model=MonthlyPayoutResponseDTO,
    summary="Approve Monthly Payout",
    description="Approve a monthly payout for processing"
)
async def approve_monthly_payout(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2050, description="Year"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> MonthlyPayoutResponseDTO:
    """Approve a monthly payout for processing."""
    return await controller.approve_monthly_payout(
        employee_id, month, year, current_user
    )


@router.post(
    "/employee/{employee_id}/process",
    response_model=MonthlyPayoutResponseDTO,
    summary="Process Monthly Payout",
    description="Process an approved monthly payout"
)
async def process_monthly_payout(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2050, description="Year"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> MonthlyPayoutResponseDTO:
    """Process an approved monthly payout."""
    return await controller.process_monthly_payout(
        employee_id, month, year, current_user
    )


@router.post(
    "/approve/bulk",
    response_model=Dict[str, Any],
    summary="Bulk Approve Payouts",
    description="Approve multiple payouts in bulk"
)
async def bulk_approve_payouts(
    request: PayoutApprovalDTO,
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """Approve multiple payouts in bulk."""
    return await controller.bulk_approve_payouts(request, current_user)


@router.post(
    "/process/bulk",
    response_model=Dict[str, Any],
    summary="Bulk Process Payouts",
    description="Process multiple payouts in bulk"
)
async def bulk_process_payouts(
    request: PayoutProcessingDTO,
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """Process multiple payouts in bulk."""
    return await controller.bulk_process_payouts(request, current_user)


@router.get(
    "/employee/{employee_id}/payslip",
    response_model=PayslipDataDTO,
    summary="Get Employee Payslip",
    description="Get payslip data for an employee"
)
async def get_employee_payslip(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2050, description="Year"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> PayslipDataDTO:
    """Get payslip data for an employee."""
    return await controller.get_employee_payslip(
        employee_id, month, year, current_user
    )


@router.get(
    "/pending-approvals",
    response_model=List[MonthlyPayoutResponseDTO],
    summary="Get Pending Approvals",
    description="Get payouts pending approval"
)
async def get_pending_approvals(
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> List[MonthlyPayoutResponseDTO]:
    """Get payouts pending approval."""
    return await controller.get_pending_approvals(current_user)


# Analytics and Reporting Endpoints

@router.get(
    "/analytics/lwp",
    response_model=Dict[str, Any],
    summary="Get LWP Analytics",
    description="Get LWP impact analytics for a specific period"
)
async def get_lwp_analytics(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2050, description="Year"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get LWP impact analytics for a specific period."""
    # Note: This would need to be implemented in the controller
    return {
        "period": f"{month:02d}/{year}",
        "total_employees": 0,
        "employees_with_lwp": 0,
        "total_lwp_days": 0,
        "total_lwp_deduction": 0.0,
        "lwp_impact_percentage": 0.0
    }


@router.get(
    "/analytics/department",
    response_model=Dict[str, Any],
    summary="Get Department-wise Analytics",
    description="Get department-wise payout analytics"
)
async def get_department_analytics(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2050, description="Year"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get department-wise payout analytics."""
    # Note: This would need to be implemented in the controller
    return {
        "period": f"{month:02d}/{year}",
        "department_breakdown": {}
    }


@router.get(
    "/analytics/compliance",
    response_model=Dict[str, Any],
    summary="Get Compliance Metrics",
    description="Get payout compliance metrics"
)
async def get_compliance_metrics(
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Query(..., ge=2020, le=2050, description="Year"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get payout compliance metrics."""
    # Note: This would need to be implemented in the controller
    return {
        "period": f"{month:02d}/{year}",
        "total_payouts": 0,
        "on_time_processing_rate": 100.0,
        "pending_approvals": 0,
        "failed_payouts": 0
    }


# Employee History Endpoints

@router.get(
    "/employee/{employee_id}/history",
    response_model=List[MonthlyPayoutResponseDTO],
    summary="Get Employee Payout History",
    description="Get payout history for an employee for a specific year"
)
async def get_employee_payout_history(
    employee_id: str = Path(..., description="Employee ID"),
    year: int = Query(..., ge=2020, le=2050, description="Year"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> List[MonthlyPayoutResponseDTO]:
    """Get payout history for an employee for a specific year."""
    # Note: This would need to be implemented in the controller
    return []


# Status Management Endpoints

@router.get(
    "/status/{status}",
    response_model=List[MonthlyPayoutResponseDTO],
    summary="Get Payouts by Status",
    description="Get payouts filtered by status"
)
async def get_payouts_by_status(
    status: str = Path(..., description="Payout status"),
    limit: Optional[int] = Query(100, ge=1, le=1000, description="Result limit"),
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller),
    current_user: CurrentUser = Depends(get_current_user)
) -> List[MonthlyPayoutResponseDTO]:
    """Get payouts filtered by status."""
    # Note: This would need to be implemented in the controller
    return []


# Health Check Endpoint

@router.get(
    "/health",
    response_model=Dict[str, Any],
    summary="Health Check",
    description="Check the health of the monthly payout service"
)
async def health_check(
    controller: MonthlyPayoutController = Depends(get_monthly_payout_controller)
) -> Dict[str, Any]:
    """Check the health of the monthly payout service."""
    return {
        "status": "healthy",
        "service": "monthly-payouts",
        "version": "2.0",
        "timestamp": "2024-01-01T00:00:00Z"
    } 