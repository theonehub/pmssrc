"""
SOLID-Compliant Taxation Routes v2 (Minimal)
Clean architecture implementation of minimal taxation HTTP endpoints
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from datetime import date, datetime

from app.api.controllers.taxation_controller import TaxationController
from app.application.dto.taxation_dto import (
    TaxCalculationRequestDTO,
    TaxationUpdateRequestDTO,
    TaxSearchFiltersDTO,
    TaxationResponseDTO,
    TaxationValidationError,
    TaxationBusinessRuleError,
    TaxationNotFoundError
)
from app.config.dependency_container import get_dependency_container
from app.auth.auth_dependencies import CurrentUser, get_current_user, require_role

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/taxation-minimal", tags=["taxation-v2-minimal"])

def get_taxation_controller() -> TaxationController:
    """Get taxation controller instance."""
    try:
        container = get_dependency_container()
        return container.get_taxation_controller()
    except Exception as e:
        logger.warning(f"Could not get taxation controller from container: {e}")
        return TaxationController()

# Health check endpoint
@router.get("/health")
async def health_check(
    controller: TaxationController = Depends(get_taxation_controller)
) -> Dict[str, str]:
    """Health check for taxation service."""
    return await controller.health_check()

# Taxation calculation endpoints
@router.post("/calculate", response_model=TaxationResponseDTO)
async def calculate_taxation(
    request: TaxCalculationRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    role: str = Depends(require_role("admin")),
    controller: TaxationController = Depends(get_taxation_controller)
) -> TaxationResponseDTO:
    """Calculate taxation for an employee."""
    try:
        logger.info(f"Calculating taxation for employee {request.employee_id}")
        return await controller.calculate_taxation(request, current_user.hostname)
    except Exception as e:
        logger.error(f"Error calculating taxation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Basic taxation endpoints
@router.get("/all-taxation")
async def get_all_taxation(
    tax_year: Optional[str] = Query(None, description="Filter by tax year"),
    filing_status: Optional[str] = Query(None, description="Filter by filing status"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get all taxation records with optional filters.
    Frontend expects this endpoint for taxationService.getAllTaxation()
    """
    # Mock response matching frontend expectations
    return [
        {
            "employee_id": "EMP001",
            "employee_name": "John Doe",
            "tax_year": "2024-2025",
            "filing_status": "pending",
            "total_tax_liability": 50000,
            "salary_components": {
                "basic": 500000,
                "hra": 200000,
                "special_allowance": 100000
            },
            "deductions": {
                "section_80c": 150000,
                "section_80d": 25000
            },
            "regime": "old",
            "last_updated": datetime.now().isoformat()
        }
    ]

@router.get("/taxation/{employee_id}")
async def get_taxation_by_employee_id(
    employee_id: str = Path(..., description="Employee ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get taxation data for a specific employee.
    Frontend expects this endpoint for taxationService.getTaxationByEmpId()
    """
    # Mock response matching frontend expectations
    return {
        "employee_id": employee_id,
        "employee_name": "John Doe",
        "tax_year": "2024-2025",
        "filing_status": "pending",
        "regime": "old",
        "salary_components": {
            "basic": 500000,
            "hra": 200000,
            "special_allowance": 100000
        },
        "perquisites": {},
        "other_sources": {},
        "deductions": {
            "section_80c": 150000,
            "section_80d": 25000
        },
        "tax_calculation": {
            "gross_total_income": 800000,
            "total_deductions": 175000,
            "taxable_income": 625000,
            "tax_liability": 50000
        },
        "last_updated": datetime.now().isoformat()
    }

@router.post("/taxation")
async def save_taxation_data(
    taxation_data: Dict[str, Any] = Body(..., description="Taxation data to save"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Save taxation data.
    Frontend expects this endpoint for taxationService.saveTaxationData()
    """
    # Mock save response
    return {
        "success": True,
        "message": "Taxation data saved successfully",
        "employee_id": taxation_data.get("employee_id"),
        "tax_year": taxation_data.get("tax_year", "2024-2025"),
        "updated_at": datetime.now().isoformat(),
        "updated_by": current_user.get("sub", "system")
    }

@router.put("/taxation/{employee_id}")
async def update_taxation(
    employee_id: str = Path(..., description="Employee ID"),
    taxation_data: Dict[str, Any] = Body(..., description="Updated taxation data"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update taxation data for an employee.
    """
    # Mock update response
    return {
        "success": True,
        "message": "Taxation data updated successfully",
        "employee_id": employee_id,
        "updated_at": datetime.now().isoformat(),
        "updated_by": current_user.get("sub", "system")
    }

@router.delete("/taxation/{employee_id}")
async def delete_taxation(
    employee_id: str = Path(..., description="Employee ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Delete taxation data for an employee.
    Frontend expects this endpoint for taxationService.deleteTaxation()
    """
    # Mock delete response
    return {
        "success": True,
        "message": "Taxation data deleted successfully",
        "employee_id": employee_id,
        "deleted_at": datetime.now().isoformat(),
        "deleted_by": current_user.get("sub", "system")
    }

@router.get("/my-taxation")
async def get_my_taxation(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get taxation data for the current user.
    Frontend expects this endpoint for taxationService.getMyTaxation()
    """
    employee_id = current_user.get("sub", "EMP001")
    
    # Mock response for current user
    return {
        "employee_id": employee_id,
        "employee_name": "Current User",
        "tax_year": "2024-2025",
        "filing_status": "pending",
        "regime": "old",
        "salary_components": {
            "basic": 500000,
            "hra": 200000,
            "special_allowance": 100000
        },
        "deductions": {
            "section_80c": 150000,
            "section_80d": 25000
        },
        "tax_calculation": {
            "total_tax_liability": 50000
        },
        "last_updated": datetime.now().isoformat()
    }

@router.post("/update-tax-payment/{employee_id}")
async def update_tax_payment(
    employee_id: str = Path(..., description="Employee ID"),
    request: Dict[str, Any] = Body(..., description="Tax payment update"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update tax payment amount.
    Frontend expects this endpoint for taxationService.updateTaxPayment()
    """
    amount_paid = request.get("amount_paid", 0)
    
    return {
        "success": True,
        "message": "Tax payment updated successfully",
        "employee_id": employee_id,
        "amount_paid": amount_paid,
        "updated_at": datetime.now().isoformat()
    }

@router.post("/update-filing-status/{employee_id}")
async def update_filing_status(
    employee_id: str = Path(..., description="Employee ID"),
    request: Dict[str, Any] = Body(..., description="Filing status update"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update filing status.
    Frontend expects this endpoint for taxationService.updateFilingStatus()
    """
    status = request.get("status", "pending")
    
    return {
        "success": True,
        "message": "Filing status updated successfully",
        "employee_id": employee_id,
        "filing_status": status,
        "updated_at": datetime.now().isoformat()
    }

@router.post("/save-taxation-data")
async def save_taxation_data_alt(
    taxation_data: Dict[str, Any] = Body(..., description="Taxation data to save"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Save taxation data (alternative endpoint).
    Frontend expects this endpoint for taxationService.saveTaxationData()
    """
    # Mock save response
    return {
        "success": True,
        "message": "Taxation data saved successfully",
        "employee_id": taxation_data.get("employee_id"),
        "tax_year": taxation_data.get("tax_year", "2024-2025"),
        "updated_at": datetime.now().isoformat(),
        "updated_by": current_user.get("sub", "system")
    }

@router.post("/compute-vrs-value/{employee_id}")
async def compute_vrs_value(
    employee_id: str = Path(..., description="Employee ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Compute VRS value.
    Frontend expects this endpoint for taxationService.computeVrsValue()
    """
    # Mock VRS calculation
    vrs_value = 125000  # Mock value
    
    return {
        "employee_id": employee_id,
        "vrs_value": vrs_value,
        "calculated_at": datetime.now().isoformat()
    } 