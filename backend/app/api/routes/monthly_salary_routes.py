"""
Monthly Salary API Routes
Production-ready REST API endpoints for monthly salary operations
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from datetime import datetime

# Import centralized logger
from app.utils.logger import get_logger

from app.auth.auth_dependencies import get_current_user, CurrentUser
from app.application.dto.taxation_dto import (
    # Monthly Salary DTOs
    MonthlySalaryDTO,
    MonthlySalaryComputeRequest,
    MonthlySalaryBulkComputeRequest,
    MonthlySalaryBulkComputeResponse,
    MonthlySalaryListResponse,
    MonthlySalarySummaryResponse,
    MonthlySalaryStatusUpdateRequest,
    MonthlySalaryPaymentRequest
)
from app.api.controllers.taxation_controller import UnifiedTaxationController
from app.config.dependency_container import (
    get_taxation_controller
)
from app.domain.exceptions.taxation_exceptions import (
    TaxationRecordNotFoundError,
    TaxationValidationError,
    TaxCalculationError,
    FinalizedRecordError,
    DuplicateTaxationRecordError
)

# Configure logger
logger = get_logger(__name__)

router = APIRouter(prefix="/api/v2/monthly-salary", tags=["monthly-salary"])

# =============================================================================
# MONTHLY SALARY COMPUTATION ENDPOINTS
# =============================================================================

@router.post("/compute", response_model=MonthlySalaryDTO)
async def compute_monthly_salary_v2(
    request: MonthlySalaryComputeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
):
    """Compute monthly salary for an employee."""
    try:
        return await controller.compute_monthly_salary(
            request.employee_id,
            request.month,
            request.year,
            current_user
        )
    except TaxationRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TaxationValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error computing monthly salary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/bulk-compute", response_model=MonthlySalaryBulkComputeResponse)
async def bulk_compute_monthly_salaries(
    request: MonthlySalaryBulkComputeRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
):
    """Bulk compute monthly salaries for multiple employees."""
    try:
        return await controller.bulk_compute_monthly_salaries(
            request,
            current_user
        )
    except TaxationValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error bulk computing monthly salaries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# MONTHLY SALARY QUERY ENDPOINTS
# =============================================================================

@router.get("/period/month/{month}/year/{year}", response_model=MonthlySalaryListResponse)
async def get_monthly_salaries_for_period(
    month: int,
    year: int,
    status: Optional[str] = None,
    department: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
):
    """Get monthly salaries for a specific period."""
    try:
        return await controller.get_monthly_salaries_for_period(
            month, year, status, department, skip, limit, current_user
        )
    except Exception as e:
        logger.error(f"Error getting monthly salaries for period: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/summary/month/{month}/year/{year}", response_model=MonthlySalarySummaryResponse)
async def get_monthly_salary_summary(
    month: int,
    year: int,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
):
    """Get monthly salary summary for a specific period."""
    try:
        return await controller.get_monthly_salary_summary(
            month, year, current_user
        )
    except Exception as e:
        logger.error(f"Error getting monthly salary summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/employee/{employee_id}/month/{month}/year/{year}", response_model=MonthlySalaryDTO)
async def get_monthly_salary(
    employee_id: str,
    month: int,
    year: int,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
):
    """Get monthly salary for a specific employee and period."""
    try:
        return await controller.get_monthly_salary(
            employee_id, month, year, current_user
        )
    except TaxationRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting monthly salary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# MONTHLY SALARY UPDATE ENDPOINTS
# =============================================================================

@router.put("/status", response_model=MonthlySalaryDTO)
async def update_monthly_salary_status(
    request: MonthlySalaryStatusUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
):
    """Update monthly salary status."""
    try:
        return await controller.update_monthly_salary_status(
            request,
            current_user
        )
    except TaxationRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TaxationValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating monthly salary status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/payment", response_model=MonthlySalaryDTO)
async def mark_salary_payment(
    request: MonthlySalaryPaymentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
):
    """Mark salary payment."""
    try:
        return await controller.mark_salary_payment(
            request,
            current_user
        )
    except TaxationRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TaxationValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error marking salary payment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# MONTHLY SALARY DELETE ENDPOINTS
# =============================================================================

@router.delete("/employee/{employee_id}/month/{month}/year/{year}")
async def delete_monthly_salary(
    employee_id: str,
    month: int,
    year: int,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
):
    """Delete monthly salary record."""
    try:
        await controller.delete_monthly_salary(
            employee_id, month, year, current_user
        )
        return {"message": "Monthly salary deleted successfully"}
    except TaxationRecordNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FinalizedRecordError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting monthly salary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 