"""
Monthly Salary Routes
FastAPI routes for monthly salary operations
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Path

from app.api.controllers.monthly_salary_controller import MonthlySalaryController
from app.application.dto.monthly_salary_dto import (
    MonthlySalaryResponseDTO,
    MonthlySalaryListResponseDTO,
    MonthlySalaryComputeRequestDTO,
    MonthlySalaryBulkComputeRequestDTO,
    MonthlySalaryBulkComputeResponseDTO,
    MonthlySalaryStatusUpdateRequestDTO,
    MonthlySalarySummaryDTO
)
from app.auth.auth_dependencies import CurrentUser, get_current_user
from app.config.dependency_container import get_monthly_salary_controller


# Create router
router = APIRouter(
    prefix="/api/v2/monthly-salary",
    tags=["Monthly Salary Processing"],
    responses={404: {"description": "Not found"}}
)


@router.get(
    "/employee/{employee_id}/month/{month}/year/{year}",
    response_model=MonthlySalaryResponseDTO,
    summary="Get Monthly Salary",
    description="""
    Get monthly salary for a specific employee, month, and year.
    
    **Data Flow Sequence:**
    1. Fetch employee details from user_service_impl
    2. Get monthly salary info from "monthly_salary" MongoDB collection for current month/year
    3. If no monthly salary data exists, fallback to taxation_records via tax_calculation_service
    4. Return pre-calculated monthly_salary as "monthly_payroll: Optional[PayoutMonthlyProjection]" with "not yet computed" status
    
    **Parameters:**
    - **employee_id**: Employee ID
    - **month**: Month (1-12)
    - **year**: Year
    
    **Returns:**
    - Monthly salary data with all components, deductions, and employee details
    - If no computed salary exists, returns taxation-based projection with "not_computed" status
    """
)
async def get_monthly_salary(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2020, le=2030, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: MonthlySalaryController = Depends(get_monthly_salary_controller)
) -> MonthlySalaryResponseDTO:
    """Get monthly salary for an employee."""
    return await controller.get_monthly_salary(
        employee_id=employee_id,
        month=month,
        year=year,
        current_user=current_user
    )


@router.get(
    "/period/month/{month}/year/{year}",
    response_model=MonthlySalaryListResponseDTO,
    summary="Get Monthly Salaries for Period",
    description="""
    Get all monthly salaries for a specific month and year.
    
    **Parameters:**
    - **month**: Month (1-12)
    - **year**: Year
    - **status**: Optional status filter (not_computed, pending, computed, approved, paid, rejected)
    - **department**: Optional department filter
    - **skip**: Number of records to skip (pagination)
    - **limit**: Number of records to return (max 1000)
    
    **Returns:**
    - List of monthly salaries with pagination info
    - Includes employee details for each salary record
    """
)
async def get_monthly_salaries_for_period(
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2020, le=2030, description="Year"),
    status: Optional[str] = Query(None, description="Status filter"),
    department: Optional[str] = Query(None, description="Department filter"),
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(50, ge=1, le=1000, description="Limit records"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: MonthlySalaryController = Depends(get_monthly_salary_controller)
) -> MonthlySalaryListResponseDTO:
    """Get all monthly salaries for a period."""
    return await controller.get_monthly_salaries_for_period(
        month=month,
        year=year,
        current_user=current_user,
        status_filter=status,
        department=department,
        skip=skip,
        limit=limit
    )


@router.post(
    "/compute",
    response_model=MonthlySalaryResponseDTO,
    summary="Compute Monthly Salary",
    description="""
    Compute monthly salary for a specific employee.
    
    **Process:**
    1. Validates employee exists and has taxation record
    2. Retrieves or calculates tax computation from taxation service
    3. Creates monthly payout projection using tax_calculation_service._create_monthly_payout_from_taxation_record()
    4. Saves computed salary to monthly_salary collection
    5. Marks status as "computed"
    
    **Request Body:**
    - **employee_id**: Employee ID
    - **month**: Month (1-12)
    - **year**: Year
    - **tax_year**: Tax year (e.g., '2023-24')
    - **force_recompute**: Whether to recompute if already computed
    - **computed_by**: Optional - user who triggered computation
    
    **Returns:**
    - Computed monthly salary with all details
    """
)
async def compute_monthly_salary(
    request: MonthlySalaryComputeRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: MonthlySalaryController = Depends(get_monthly_salary_controller)
) -> MonthlySalaryResponseDTO:
    """Compute monthly salary for an employee."""
    return await controller.compute_monthly_salary(
        request=request,
        current_user=current_user
    )


@router.post(
    "/bulk-compute",
    response_model=MonthlySalaryBulkComputeResponseDTO,
    summary="Bulk Compute Monthly Salaries",
    description="""
    Bulk compute monthly salaries for multiple employees.
    
    **Process:**
    1. If employee_ids not provided, processes all active employees in organization
    2. For each employee, follows same computation process as individual compute
    3. Skips already computed salaries unless force_recompute is true
    4. Returns summary of successful, failed, and skipped computations
    
    **Request Body:**
    - **month**: Month (1-12)
    - **year**: Year
    - **tax_year**: Tax year (e.g., '2023-24')
    - **employee_ids**: Optional list of specific employee IDs (if None, processes all)
    - **force_recompute**: Whether to recompute already computed salaries
    - **computed_by**: Optional - user who triggered computation
    
    **Returns:**
    - Summary with counts of successful, failed, and skipped computations
    - List of errors for failed computations
    - Overall computation summary statistics
    """
)
async def bulk_compute_monthly_salaries(
    request: MonthlySalaryBulkComputeRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: MonthlySalaryController = Depends(get_monthly_salary_controller)
) -> MonthlySalaryBulkComputeResponseDTO:
    """Bulk compute monthly salaries."""
    return await controller.bulk_compute_monthly_salaries(
        request=request,
        current_user=current_user
    )


@router.put(
    "/status",
    response_model=MonthlySalaryResponseDTO,
    summary="Update Monthly Salary Status",
    description="""
    Update the processing status of a monthly salary record.
    
    **Status Values:**
    - **not_computed**: Initial state, no computation done
    - **pending**: Computation in progress
    - **computed**: Computation completed, ready for review
    - **approved**: Approved by manager/admin, ready for payment
    - **paid**: Payment processed
    - **rejected**: Rejected, needs revision
    
    **Request Body:**
    - **employee_id**: Employee ID
    - **month**: Month (1-12)
    - **year**: Year
    - **status**: New status value
    - **notes**: Optional notes for status change
    - **updated_by**: Optional - user who updated status
    
    **Returns:**
    - Updated monthly salary record
    """
)
async def update_monthly_salary_status(
    request: MonthlySalaryStatusUpdateRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: MonthlySalaryController = Depends(get_monthly_salary_controller)
) -> MonthlySalaryResponseDTO:
    """Update monthly salary status."""
    return await controller.update_monthly_salary_status(
        request=request,
        current_user=current_user
    )


@router.get(
    "/summary/month/{month}/year/{year}",
    response_model=MonthlySalarySummaryDTO,
    summary="Get Monthly Salary Summary",
    description="""
    Get summary statistics for monthly salary processing for a specific period.
    
    **Parameters:**
    - **month**: Month (1-12)
    - **year**: Year
    
    **Returns:**
    - Total employee count and status breakdown
    - Financial summary (total gross, net, deductions, TDS)
    - Computation completion rate
    - Processing timestamps
    """
)
async def get_monthly_salary_summary(
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2020, le=2030, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: MonthlySalaryController = Depends(get_monthly_salary_controller)
) -> MonthlySalarySummaryDTO:
    """Get monthly salary summary for a period."""
    return await controller.get_monthly_salary_summary(
        month=month,
        year=year,
        current_user=current_user
    )


@router.delete(
    "/employee/{employee_id}/month/{month}/year/{year}",
    summary="Delete Monthly Salary",
    description="""
    Delete a monthly salary record.
    
    **Restrictions:**
    - Cannot delete salary records with status "paid"
    - Only admin/superadmin can delete salary records
    
    **Parameters:**
    - **employee_id**: Employee ID
    - **month**: Month (1-12)
    - **year**: Year
    
    **Returns:**
    - Success message
    """
)
async def delete_monthly_salary(
    employee_id: str = Path(..., description="Employee ID"),
    month: int = Path(..., ge=1, le=12, description="Month (1-12)"),
    year: int = Path(..., ge=2020, le=2030, description="Year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: MonthlySalaryController = Depends(get_monthly_salary_controller)
) -> dict:
    """Delete monthly salary record."""
    return await controller.delete_monthly_salary(
        employee_id=employee_id,
        month=month,
        year=year,
        current_user=current_user
    ) 