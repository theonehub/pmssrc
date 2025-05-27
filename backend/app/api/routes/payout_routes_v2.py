"""
SOLID-Compliant Payout Routes v2
Clean architecture implementation of payout HTTP endpoints
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.responses import StreamingResponse
from datetime import date, datetime
import calendar

from api.controllers.payout_controller import PayoutController
from application.dto.payroll_dto import (
    PayoutCalculationRequestDTO, PayoutCreateRequestDTO, PayoutUpdateRequestDTO,
    BulkPayoutRequestDTO, PayoutSearchFiltersDTO, PayslipGenerationRequestDTO,
    PayoutResponseDTO, PayoutSummaryResponseDTO, PayoutHistoryResponseDTO,
    BulkPayoutResponseDTO, PayslipResponseDTO, PayoutStatusEnum
)
from config.dependency_container import get_payout_controller
from auth.auth import extract_emp_id, extract_hostname, role_checker

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/payouts", tags=["payouts-v2"])

# Health check endpoint
@router.get("/health")
async def health_check(
    controller: PayoutController = Depends(get_payout_controller)
) -> Dict[str, str]:
    """Health check for payout service."""
    return await controller.health_check()

# Payout calculation endpoints
@router.post("/calculate", response_model=PayoutResponseDTO)
async def calculate_monthly_payout(
    request: PayoutCalculationRequestDTO,
    controller: PayoutController = Depends(get_payout_controller),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname),
) -> PayoutResponseDTO:
    """
    Calculate monthly payout for an employee.
    
    Args:
        request: Payout calculation request
        controller: Payout controller dependency
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        Calculated payout response
    """
    return await controller.calculate_payout(request, hostname)

# Payout CRUD endpoints
@router.post("", response_model=PayoutResponseDTO)
async def create_payout(
    request: PayoutCreateRequestDTO,
    controller: PayoutController = Depends(get_payout_controller),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname),
) -> PayoutResponseDTO:
    """
    Create a new payout record.
    
    Args:
        request: Payout creation request
        controller: Payout controller dependency
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        Created payout response
    """
    return await controller.create_payout(request, hostname)

@router.get("/employee/{employee_id}", response_model=List[PayoutResponseDTO])
async def get_employee_payouts(
    employee_id: str,
    year: Optional[int] = Query(None, ge=2020, le=2050, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
    controller: PayoutController = Depends(get_payout_controller),
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager", "user"])),
    hostname: str = Depends(extract_hostname),
) -> List[PayoutResponseDTO]:
    """
    Get payouts for a specific employee.
    
    Args:
        employee_id: Employee ID to get payouts for
        year: Filter by year (optional)
        month: Filter by month (optional)
        controller: Payout controller dependency
        emp_id: Current user's employee ID
        role: User role
        hostname: Organization hostname
        
    Returns:
        List of employee payouts
    """
    # Check permissions - admin/manager can access any employee, users only their own
    if role not in ["admin", "superadmin", "manager"] and emp_id != employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return await controller.get_employee_payouts(employee_id, hostname, year, month)

@router.get("/my-payouts", response_model=List[PayoutResponseDTO])
async def get_my_payouts(
    year: Optional[int] = Query(None, ge=2020, le=2050, description="Filter by year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filter by month"),
    controller: PayoutController = Depends(get_payout_controller),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname),
) -> List[PayoutResponseDTO]:
    """
    Get payouts for the current user.
    
    Args:
        year: Filter by year (optional)
        month: Filter by month (optional)
        controller: Payout controller dependency
        emp_id: Current user's employee ID
        hostname: Organization hostname
        
    Returns:
        List of current user's payouts
    """
    return await controller.get_employee_payouts(emp_id, hostname, year, month)

@router.get("/{payout_id}", response_model=PayoutResponseDTO)
async def get_payout_by_id(
    payout_id: str,
    controller: PayoutController = Depends(get_payout_controller),
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager", "user"])),
    hostname: str = Depends(extract_hostname),
) -> PayoutResponseDTO:
    """
    Get payout by ID.
    
    Args:
        payout_id: Payout ID
        controller: Payout controller dependency
        emp_id: Current user's employee ID
        role: User role
        hostname: Organization hostname
        
    Returns:
        Payout response
    """
    # Get the payout
    payout = await controller.get_payout_by_id(payout_id, hostname)
    
    # Check permissions - admin/manager can access any payout, users only their own
    if role not in ["admin", "superadmin", "manager"] and emp_id != payout.employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return payout

@router.put("/{payout_id}", response_model=PayoutResponseDTO)
async def update_payout(
    payout_id: str,
    request: PayoutUpdateRequestDTO,
    controller: PayoutController = Depends(get_payout_controller),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname),
) -> PayoutResponseDTO:
    """
    Update a payout record.
    
    Args:
        payout_id: Payout ID to update
        request: Update request data
        controller: Payout controller dependency
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        Updated payout response
    """
    return await controller.update_payout(payout_id, request, hostname)

@router.patch("/{payout_id}/status", response_model=Dict[str, Any])
async def update_payout_status(
    payout_id: str,
    status: PayoutStatusEnum = Body(..., description="New payout status"),
    controller: PayoutController = Depends(get_payout_controller),
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname),
) -> Dict[str, Any]:
    """
    Update payout status.
    
    Args:
        payout_id: Payout ID
        status: New status
        controller: Payout controller dependency
        emp_id: Current user's employee ID
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        Status update response
    """
    return await controller.update_payout_status(payout_id, status.value, emp_id, hostname)

# Bulk operations
@router.post("/bulk-process", response_model=BulkPayoutResponseDTO)
async def bulk_process_payouts(
    request: BulkPayoutRequestDTO,
    controller: PayoutController = Depends(get_payout_controller),
    role: str = Depends(role_checker(["admin", "superadmin"])),
    hostname: str = Depends(extract_hostname)
) -> BulkPayoutResponseDTO:
    """
    Process payouts for multiple employees.
    
    Args:
        request: Bulk payout request
        controller: Payout controller dependency
        role: User role (admin, superadmin)
        hostname: Organization hostname
        
    Returns:
        Bulk processing response
    """
    return await controller.bulk_process_payouts(request, hostname)

# Monthly operations
@router.get("/monthly/{year}/{month}", response_model=List[PayoutResponseDTO])
async def get_monthly_payouts(
    year: int,
    month: int,
    status: Optional[PayoutStatusEnum] = Query(None, description="Filter by status"),
    controller: PayoutController = Depends(get_payout_controller),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname)
) -> List[PayoutResponseDTO]:
    """
    Get all payouts for a specific month.
    
    Args:
        year: Year
        month: Month
        status: Filter by status (optional)
        controller: Payout controller dependency
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        List of monthly payouts
    """
    status_value = status.value if status else None
    return await controller.get_monthly_payouts(month, year, hostname, status_value)

@router.get("/summary/{year}/{month}", response_model=PayoutSummaryResponseDTO)
async def get_monthly_payout_summary(
    year: int,
    month: int,
    controller: PayoutController = Depends(get_payout_controller),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname)
) -> PayoutSummaryResponseDTO:
    """
    Get payout summary for a month.
    
    Args:
        year: Year
        month: Month
        controller: Payout controller dependency
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        Monthly payout summary
    """
    return await controller.get_monthly_payout_summary(month, year, hostname)

# Payslip operations
@router.get("/{payout_id}/payslip", response_model=PayslipResponseDTO)
async def get_payslip_data(
    payout_id: str,
    controller: PayoutController = Depends(get_payout_controller),
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager", "user"])),
    hostname: str = Depends(extract_hostname)
) -> PayslipResponseDTO:
    """
    Get payslip data for a payout.
    
    Args:
        payout_id: Payout ID
        controller: Payout controller dependency
        emp_id: Current user's employee ID
        role: User role
        hostname: Organization hostname
        
    Returns:
        Payslip data response
    """
    # First check if payout exists and user has access
    payout = await controller.get_payout_by_id(payout_id, hostname)
    
    # Check permissions - admin/manager can access any payslip, users only their own
    if role not in ["admin", "superadmin", "manager"] and emp_id != payout.employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Generate payslip request
    payslip_request = PayslipGenerationRequestDTO(payout_id=payout_id)
    return await controller.generate_payslip(payslip_request, hostname)

@router.post("/{payout_id}/payslip/generate", response_model=PayslipResponseDTO)
async def generate_payslip(
    payout_id: str,
    request: PayslipGenerationRequestDTO,
    controller: PayoutController = Depends(get_payout_controller),
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager", "user"])),
    hostname: str = Depends(extract_hostname)
) -> PayslipResponseDTO:
    """
    Generate payslip for a payout.
    
    Args:
        payout_id: Payout ID
        request: Payslip generation request
        controller: Payout controller dependency
        emp_id: Current user's employee ID
        role: User role
        hostname: Organization hostname
        
    Returns:
        Generated payslip response
    """
    # First check if payout exists and user has access
    payout = await controller.get_payout_by_id(payout_id, hostname)
    
    # Check permissions - admin/manager can access any payslip, users only their own
    if role not in ["admin", "superadmin", "manager"] and emp_id != payout.employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Ensure payout_id in request matches path parameter
    request.payout_id = payout_id
    
    return await controller.generate_payslip(request, hostname)

# History endpoints
@router.get("/history/{employee_id}/{year}", response_model=PayoutHistoryResponseDTO)
async def get_employee_payout_history(
    employee_id: str,
    year: int,
    controller: PayoutController = Depends(get_payout_controller),
    emp_id: str = Depends(extract_emp_id),
    role: str = Depends(role_checker(["admin", "superadmin", "manager", "user"])),
    hostname: str = Depends(extract_hostname)
) -> PayoutHistoryResponseDTO:
    """
    Get payout history for an employee.
    
    Args:
        employee_id: Employee ID
        year: Year
        controller: Payout controller dependency
        emp_id: Current user's employee ID
        role: User role
        hostname: Organization hostname
        
    Returns:
        Employee payout history
    """
    # Check permissions - admin/manager can access any employee, users only their own
    if role not in ["admin", "superadmin", "manager"] and emp_id != employee_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return await controller.get_employee_payout_history(employee_id, year, hostname)

@router.get("/my-history/{year}", response_model=PayoutHistoryResponseDTO)
async def get_my_payout_history(
    year: int,
    controller: PayoutController = Depends(get_payout_controller),
    emp_id: str = Depends(extract_emp_id),
    hostname: str = Depends(extract_hostname)
) -> PayoutHistoryResponseDTO:
    """
    Get payout history for the current user.
    
    Args:
        year: Year
        controller: Payout controller dependency
        emp_id: Current user's employee ID
        hostname: Organization hostname
        
    Returns:
        Current user's payout history
    """
    return await controller.get_employee_payout_history(emp_id, year, hostname)

# Auto-generation endpoint
@router.post("/auto-generate/{employee_id}", response_model=PayoutResponseDTO)
async def auto_generate_current_month_payout(
    employee_id: str,
    controller: PayoutController = Depends(get_payout_controller),
    role: str = Depends(role_checker(["admin", "superadmin", "manager"])),
    hostname: str = Depends(extract_hostname)
) -> PayoutResponseDTO:
    """
    Auto-generate payout for current month.
    
    Args:
        employee_id: Employee ID
        controller: Payout controller dependency
        role: User role (admin, superadmin, manager)
        hostname: Organization hostname
        
    Returns:
        Generated payout response
    """
    # Get current month and year
    current_date = datetime.now()
    month = current_date.month
    year = current_date.year
    
    # Create calculation request for current month
    request = PayoutCalculationRequestDTO(
        employee_id=employee_id,
        month=month,
        year=year,
        force_recalculate=True
    )
    
    return await controller.calculate_payout(request, hostname)

# Exception handlers
@router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    logger.error(f"Validation error: {exc}")
    raise HTTPException(status_code=400, detail=str(exc))

@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error: {exc.detail}")
    raise exc

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
