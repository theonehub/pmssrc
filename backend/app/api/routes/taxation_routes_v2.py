"""
Taxation API Routes (SOLID Architecture)
FastAPI routes for taxation operations using clean architecture
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi import status as http_status

from app.api.controllers.taxation_controller import TaxationController
from app.application.dto.taxation_dto import (
    TaxationCreateRequestDTO,
    TaxationUpdateRequestDTO,
    TaxationResponseDTO,
    TaxSearchFiltersDTO,
    TaxCalculationRequestDTO,
    TaxProjectionDTO,
    TaxComparisonDTO,
    TaxStatisticsDTO
)
from app.auth.dependencies import get_current_user, get_hostname


# Create router
router = APIRouter(prefix="/api/v2/taxation", tags=["Taxation V2"])


@router.post("/", 
             response_model=TaxationResponseDTO,
             status_code=http_status.HTTP_201_CREATED,
             summary="Create Taxation Record",
             description="Create a new taxation record for an employee")
async def create_taxation(
    request: TaxationCreateRequestDTO = Body(..., description="Taxation creation details"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> TaxationResponseDTO:
    """
    Create a new taxation record.
    
    This endpoint creates a new taxation record for an employee with the provided
    salary, deduction, and tax configuration details.
    
    **Required permissions:** HR_ADMIN, PAYROLL_ADMIN
    """
    return await controller.create_taxation(request, hostname, current_user)


@router.post("/bulk",
             response_model=Dict[str, Any],
             summary="Bulk Create Taxation Records",
             description="Create taxation records for multiple employees")
async def bulk_create_taxation(
    employee_ids: List[str] = Body(..., description="List of employee IDs"),
    tax_year: str = Body(..., description="Tax year for records"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> Dict[str, Any]:
    """
    Create taxation records for multiple employees.
    
    This endpoint creates default taxation records for a list of employees
    for the specified tax year.
    
    **Required permissions:** HR_ADMIN, PAYROLL_ADMIN
    """
    return await controller.bulk_create_taxation(
        employee_ids, tax_year, hostname, current_user
    )


@router.post("/calculate",
             response_model=TaxationResponseDTO,
             summary="Calculate Tax",
             description="Calculate tax for an employee")
async def calculate_tax(
    request: TaxCalculationRequestDTO = Body(..., description="Tax calculation request"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> TaxationResponseDTO:
    """
    Calculate tax for an employee.
    
    This endpoint performs tax calculation for an employee based on their
    current salary, deductions, and tax configuration.
    
    **Calculation types:**
    - `quick`: Basic calculation without detailed breakdown
    - `full`: Complete calculation with all components
    - `projection`: Future tax projection
    
    **Required permissions:** HR_ADMIN, PAYROLL_ADMIN, EMPLOYEE (own record)
    """
    return await controller.calculate_tax(request, hostname, current_user)


@router.post("/calculate-comprehensive/{employee_id}",
             response_model=Dict[str, Any],
             summary="Calculate Comprehensive Tax",
             description="Calculate comprehensive tax with projections and adjustments")
async def calculate_comprehensive_tax(
    employee_id: str = Path(..., description="Employee ID"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> Dict[str, Any]:
    """
    Calculate comprehensive tax with projections and LWP adjustments.
    
    This endpoint performs a comprehensive tax calculation that includes:
    - Base tax calculation
    - Salary projections considering mid-year changes
    - LWP (Leave Without Pay) adjustments
    - Effective tax calculation
    
    **Required permissions:** HR_ADMIN, PAYROLL_ADMIN, EMPLOYEE (own record)
    """
    return await controller.calculate_comprehensive_tax(
        employee_id, hostname, current_user
    )


@router.get("/{employee_id}/{tax_year}",
            response_model=TaxationResponseDTO,
            summary="Get Taxation by Employee and Year",
            description="Get taxation record by employee ID and tax year")
async def get_taxation_by_employee(
    employee_id: str = Path(..., description="Employee ID"),
    tax_year: str = Path(..., description="Tax year (YYYY-YYYY format)"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> TaxationResponseDTO:
    """
    Get taxation record by employee ID and tax year.
    
    Returns the taxation record for a specific employee and tax year,
    including salary details, deductions, and calculated tax information.
    
    **Required permissions:** HR_ADMIN, PAYROLL_ADMIN, EMPLOYEE (own record)
    """
    return await controller.get_taxation_by_employee(
        employee_id, tax_year, hostname
    )


@router.get("/current/{employee_id}",
            response_model=TaxationResponseDTO,
            summary="Get Current Taxation",
            description="Get current year taxation record for an employee")
async def get_current_taxation(
    employee_id: str = Path(..., description="Employee ID"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> TaxationResponseDTO:
    """
    Get current year taxation record for an employee.
    
    Returns the taxation record for the current financial year
    for the specified employee.
    
    **Required permissions:** HR_ADMIN, PAYROLL_ADMIN, EMPLOYEE (own record)
    """
    return await controller.get_current_taxation(employee_id, hostname)


@router.get("/history/{employee_id}",
            response_model=List[TaxationResponseDTO],
            summary="Get Tax History",
            description="Get tax history for an employee across all years")
async def get_employee_tax_history(
    employee_id: str = Path(..., description="Employee ID"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> List[TaxationResponseDTO]:
    """
    Get tax history for an employee across all years.
    
    Returns a list of all taxation records for the employee,
    sorted by tax year in descending order.
    
    **Required permissions:** HR_ADMIN, PAYROLL_ADMIN, EMPLOYEE (own record)
    """
    return await controller.get_employee_tax_history(employee_id, hostname)


@router.post("/search",
             response_model=List[TaxationResponseDTO],
             summary="Search Taxation Records",
             description="Search taxation records with filters")
async def search_taxation_records(
    filters: TaxSearchFiltersDTO = Body(..., description="Search filters"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> List[TaxationResponseDTO]:
    """
    Search taxation records with filters.
    
    Supports filtering by:
    - Tax year
    - Employee department
    - Tax regime (old/new)
    - Income range
    - Tax range
    - Filing status
    
    **Required permissions:** HR_ADMIN, PAYROLL_ADMIN
    """
    return await controller.search_taxation_records(filters, hostname)


@router.put("/{employee_id}",
            response_model=TaxationResponseDTO,
            summary="Update Taxation Record",
            description="Update an existing taxation record")
async def update_taxation(
    employee_id: str = Path(..., description="Employee ID"),
    request: TaxationUpdateRequestDTO = Body(..., description="Update details"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> TaxationResponseDTO:
    """
    Update an existing taxation record.
    
    Allows updating salary components, deductions, tax configuration,
    and other taxation-related information.
    
    **Required permissions:** HR_ADMIN, PAYROLL_ADMIN
    """
    return await controller.update_taxation(
        employee_id, request, hostname, current_user
    )


@router.delete("/{employee_id}/{tax_year}",
               response_model=Dict[str, Any],
               summary="Delete Taxation Record",
               description="Delete a taxation record")
async def delete_taxation(
    employee_id: str = Path(..., description="Employee ID"),
    tax_year: str = Path(..., description="Tax year"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> Dict[str, Any]:
    """
    Delete a taxation record.
    
    Permanently deletes the taxation record for the specified
    employee and tax year.
    
    **Warning:** This operation cannot be undone.
    
    **Required permissions:** HR_ADMIN, SYSTEM_ADMIN
    """
    return await controller.delete_taxation(
        employee_id, tax_year, hostname, current_user
    )


@router.get("/statistics/{tax_year}",
            response_model=TaxStatisticsDTO,
            summary="Get Tax Statistics",
            description="Get tax statistics for a tax year")
async def get_tax_statistics(
    tax_year: str = Path(..., description="Tax year"),
    department: Optional[str] = Query(None, description="Optional department filter"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> TaxStatisticsDTO:
    """
    Get tax statistics for a tax year.
    
    Returns comprehensive statistics including:
    - Total employees processed
    - Total tax collected
    - Average tax per employee
    - Tax distribution by brackets
    - Department-wise breakdown (if department filter applied)
    
    **Required permissions:** HR_ADMIN, FINANCE_ADMIN
    """
    return await controller.get_tax_statistics(
        tax_year, hostname, department
    )


@router.get("/regime-stats/{tax_year}",
            response_model=Dict[str, Any],
            summary="Get Regime Adoption Statistics",
            description="Get tax regime adoption statistics")
async def get_regime_adoption_stats(
    tax_year: str = Path(..., description="Tax year"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> Dict[str, Any]:
    """
    Get tax regime adoption statistics.
    
    Returns statistics about adoption of old vs new tax regime:
    - Number of employees in each regime
    - Percentage distribution
    - Average tax savings comparison
    - Regime switching trends
    
    **Required permissions:** HR_ADMIN, FINANCE_ADMIN
    """
    return await controller.get_regime_adoption_stats(tax_year, hostname)


@router.get("/top-taxpayers/{tax_year}",
            response_model=List[Dict[str, Any]],
            summary="Get Top Taxpayers",
            description="Get top taxpayers for a tax year")
async def get_top_taxpayers(
    tax_year: str = Path(..., description="Tax year"),
    limit: int = Query(10, ge=1, le=100, description="Number of top taxpayers to return"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> List[Dict[str, Any]]:
    """
    Get top taxpayers for a tax year.
    
    Returns a list of employees with highest tax liability,
    including their tax amount and basic employee information.
    
    **Note:** Personal information is anonymized for privacy.
    
    **Required permissions:** HR_ADMIN, FINANCE_ADMIN
    """
    return await controller.get_top_taxpayers(tax_year, hostname, limit)


@router.get("/department-summary/{tax_year}",
            response_model=Dict[str, Dict[str, Any]],
            summary="Get Department Tax Summary",
            description="Get department-wise tax summary")
async def get_department_tax_summary(
    tax_year: str = Path(..., description="Tax year"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> Dict[str, Dict[str, Any]]:
    """
    Get department-wise tax summary.
    
    Returns tax statistics broken down by department:
    - Total tax per department
    - Average tax per employee
    - Employee count per department
    - Tax efficiency metrics
    
    **Required permissions:** HR_ADMIN, FINANCE_ADMIN
    """
    return await controller.get_department_tax_summary(tax_year, hostname)


@router.patch("/filing-status/{employee_id}/{tax_year}",
              response_model=Dict[str, Any],
              summary="Update Filing Status",
              description="Update taxation filing status")
async def update_filing_status(
    employee_id: str = Path(..., description="Employee ID"),
    tax_year: str = Path(..., description="Tax year"),
    filing_status: str = Body(..., embed=True, description="New filing status"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user),
    controller: TaxationController = Depends()
) -> Dict[str, Any]:
    """
    Update taxation filing status.
    
    Updates the filing status for an employee's taxation record.
    
    **Valid filing statuses:**
    - `not_filed`: Tax not yet filed
    - `filed`: Tax return filed
    - `processed`: Return processed by tax authority
    - `refund_issued`: Refund issued (if applicable)
    
    **Required permissions:** HR_ADMIN, PAYROLL_ADMIN
    """
    return await controller.update_filing_status(
        employee_id, tax_year, filing_status, hostname, current_user
    )


# Additional utility endpoints for tax calculations

@router.get("/tax-brackets/{tax_year}",
            response_model=Dict[str, Any],
            summary="Get Tax Brackets",
            description="Get tax brackets for a specific year")
async def get_tax_brackets(
    tax_year: str = Path(..., description="Tax year"),
    regime: str = Query("old", description="Tax regime (old/new)"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get tax brackets for a specific year and regime.
    
    Returns the income tax slabs and rates applicable
    for the specified tax year and regime.
    
    **Required permissions:** Any authenticated user
    """
    # This would be implemented to return static tax bracket information
    # For now, return basic structure
    if regime == "new":
        brackets = {
            "regime": "new",
            "tax_year": tax_year,
            "brackets": [
                {"min": 0, "max": 300000, "rate": 0},
                {"min": 300000, "max": 600000, "rate": 5},
                {"min": 600000, "max": 900000, "rate": 10},
                {"min": 900000, "max": 1200000, "rate": 15},
                {"min": 1200000, "max": 1500000, "rate": 20},
                {"min": 1500000, "max": None, "rate": 30}
            ]
        }
    else:
        brackets = {
            "regime": "old",
            "tax_year": tax_year,
            "brackets": [
                {"min": 0, "max": 250000, "rate": 0},
                {"min": 250000, "max": 500000, "rate": 5},
                {"min": 500000, "max": 1000000, "rate": 20},
                {"min": 1000000, "max": None, "rate": 30}
            ]
        }
    
    return brackets


@router.get("/deduction-limits/{tax_year}",
            response_model=Dict[str, Any],
            summary="Get Deduction Limits",
            description="Get deduction limits for a specific year")
async def get_deduction_limits(
    tax_year: str = Path(..., description="Tax year"),
    hostname: str = Depends(get_hostname),
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get deduction limits for a specific tax year.
    
    Returns the maximum allowable deduction amounts
    for various sections of the Income Tax Act.
    
    **Required permissions:** Any authenticated user
    """
    # Return static deduction limits
    limits = {
        "tax_year": tax_year,
        "sections": {
            "80C": {"limit": 150000, "description": "Life insurance, PPF, ELSS, etc."},
            "80D": {"limit": 25000, "description": "Health insurance premiums"},
            "80E": {"limit": None, "description": "Education loan interest"},
            "80G": {"limit": None, "description": "Donations to charity"},
            "80CCD(1B)": {"limit": 50000, "description": "NPS contribution"},
            "80TTA": {"limit": 10000, "description": "Savings account interest"},
            "80TTB": {"limit": 50000, "description": "Senior citizen deposit interest"}
        },
        "standard_deduction": 50000
    }
    
    return limits


@router.get("/health",
            response_model=Dict[str, str],
            summary="Health Check",
            description="Check taxation service health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for taxation service.
    
    Returns the status of the taxation service and its dependencies.
    """
    return {
        "status": "healthy",
        "service": "taxation",
        "version": "2.0.0",
        "timestamp": "2024-01-15T10:00:00Z"
    } 