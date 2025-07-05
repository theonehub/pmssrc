"""
Comprehensive Taxation API Routes
Production-ready REST API endpoints for all taxation operations and income types
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from datetime import datetime

# Import centralized logger
from app.utils.logger import get_logger

from app.auth.auth_dependencies import get_current_user, CurrentUser
from app.application.dto.taxation_dto import (
    # Comprehensive DTOs
    PerquisitesDTO,
    HousePropertyIncomeDTO,
    CapitalGainsIncomeDTO,
    RetirementBenefitsDTO,
    # Employee Selection DTOs
    EmployeeSelectionQuery,
    EmployeeSelectionResponse,
    
    # Individual Component Update DTOs
    ComponentUpdateResponse,
    UpdateSalaryComponentRequest,
    UpdatePerquisitesComponentRequest,
    UpdateDeductionsComponentRequest,
    UpdateHousePropertyComponentRequest,
    UpdateCapitalGainsComponentRequest,
    UpdateRetirementBenefitsComponentRequest,
    UpdateOtherIncomeComponentRequest,
    UpdateMonthlyPayrollComponentRequest,
    UpdateRegimeComponentRequest,
    
    # Component Retrieval DTOs
    ComponentResponse,
    TaxationRecordStatusResponse,
    
    # Monthly Salary DTOs
    MonthlySalaryComputeRequestDTO,
    MonthlySalaryResponseDTO
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
from app.domain.services.taxation.tax_calculation_service import TaxCalculationResult

# Configure logger
logger = get_logger(__name__)

router = APIRouter(prefix="/api/v2/taxation", tags=["taxation"])

# =============================================================================
# INDIVIDUAL INCOME COMPONENT CALCULATIONS
# =============================================================================

@router.post("/perquisites/calculate",
             response_model=Dict[str, Any],
             status_code=status.HTTP_200_OK,
             summary="Calculate perquisites tax",
             description="Calculate tax impact of perquisites only")
async def calculate_perquisites(
    perquisites: PerquisitesDTO,
    regime_type: str = Query(..., description="Tax regime: 'old' or 'new'"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> Dict[str, Any]:
    """Calculate perquisites tax impact only."""
    
    try:
        response = await controller.calculate_perquisites_only(
            perquisites, regime_type, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate perquisites: {str(e)}"
        )


@router.post("/house-property/calculate",
             response_model=Dict[str, Any],
             status_code=status.HTTP_200_OK,
             summary="Calculate house property income",
             description="Calculate income from house property")
async def calculate_house_property(
    house_property_income: HousePropertyIncomeDTO,
    regime_type: str = Query(..., description="Tax regime: 'old' or 'new'"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> Dict[str, Any]:
    """Calculate house property income tax."""
    
    try:
        response = await controller.calculate_house_property_income_only(
            house_property_income, regime_type, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate house property income: {str(e)}"
        )


@router.post("/capital-gains/calculate",
             response_model=Dict[str, Any],
             status_code=status.HTTP_200_OK,
             summary="Calculate capital gains tax",
             description="Calculate capital gains tax for all types")
async def calculate_capital_gains(
    capital_gains: CapitalGainsIncomeDTO,
    regime_type: str = Query(..., description="Tax regime: 'old' or 'new'"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> Dict[str, Any]:
    """Calculate capital gains tax."""
    
    try:
        response = await controller.calculate_capital_gains_only(
            capital_gains, regime_type, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate capital gains: {str(e)}"
        )


@router.post("/retirement-benefits/calculate",
             response_model=Dict[str, Any],
             status_code=status.HTTP_200_OK,
             summary="Calculate retirement benefits tax",
             description="Calculate tax on all retirement benefits")
async def calculate_retirement_benefits(
    retirement_benefits: RetirementBenefitsDTO,
    regime_type: str = Query(..., description="Tax regime: 'old' or 'new'"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> Dict[str, Any]:
    """Calculate retirement benefits tax."""
    
    try:
        response = await controller.calculate_retirement_benefits_only(
            retirement_benefits, regime_type, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate retirement benefits: {str(e)}"
        )

# =============================================================================
# INDIVIDUAL COMPONENT UPDATE ENDPOINTS
# =============================================================================

@router.put("/records/employee/{employee_id}/salary",
            response_model=ComponentUpdateResponse,
            status_code=status.HTTP_200_OK,
            summary="Update salary component individually",
            description="Update salary income component for a specific employee and tax year")
async def update_salary_component(
    employee_id: str,
    request: UpdateSalaryComponentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComponentUpdateResponse:
    """Update salary component individually."""
    
    logger.info(f"Updating salary component for employee {employee_id} and tax year {request.tax_year}")
    
    try:
        # Ensure employee_id in path matches request
        if request.employee_id != employee_id:
            logger.error(f"Employee ID mismatch: path={employee_id}, body={request.employee_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID in path must match employee_id in request body"
            )
        
        response = await controller.update_salary_component(
            request, current_user.hostname
        )
        logger.info(f"Successfully updated salary component for employee {employee_id}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error updating salary component: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update salary component for employee {employee_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update salary component: {str(e)}"
        )


@router.put("/records/employee/{employee_id}/perquisites",
            response_model=ComponentUpdateResponse,
            status_code=status.HTTP_200_OK,
            summary="Update perquisites component individually",
            description="Update perquisites component for a specific employee and tax year")
async def update_perquisites_component(
    employee_id: str,
    request: UpdatePerquisitesComponentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComponentUpdateResponse:
    """Update perquisites component individually."""
    
    try:
        # Ensure employee_id in path matches request
        if request.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID in path must match employee_id in request body"
            )
        
        response = await controller.update_perquisites_component(
            request, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update perquisites component: {str(e)}"
        )


@router.put("/records/employee/{employee_id}/deductions",
            response_model=ComponentUpdateResponse,
            status_code=status.HTTP_200_OK,
            summary="Update deductions component individually",
            description="Update deductions component for a specific employee and tax year")
async def update_deductions_component(
    employee_id: str,
    request: UpdateDeductionsComponentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComponentUpdateResponse:
    """Update deductions component individually for a specific employee and tax year."""
    
    logger.info(f"Starting individual deductions component update for employee {employee_id}")
    logger.debug(f"Deductions update request: tax_year={request.tax_year}, notes={request.notes}")
    
    try:
        # Validate employee_id in request matches URL parameter
        if request.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee ID mismatch: URL parameter '{employee_id}' does not match request body '{request.employee_id}'"
            )
        
        response = await controller.update_deductions_component(request, current_user.hostname)
        
        logger.info(f"Successfully updated deductions component for employee {employee_id}")
        return response
        
    except TaxationRecordNotFoundError as e:
        logger.warning(f"Taxation record not found for employee {employee_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except TaxationValidationError as e:
        logger.error(f"Validation error in deductions update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except FinalizedRecordError as e:
        logger.warning(f"Attempted to update finalized record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update deductions component for employee {employee_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update deductions component: {str(e)}"
        )


@router.put("/records/employee/{employee_id}/house-property",
            response_model=ComponentUpdateResponse,
            status_code=status.HTTP_200_OK,
            summary="Update house property component individually",
            description="Update house property income component for a specific employee and tax year")
async def update_house_property_component(
    employee_id: str,
    request: UpdateHousePropertyComponentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComponentUpdateResponse:
    """Update house property component individually."""
    
    try:
        # Ensure employee_id in path matches request
        if request.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID in path must match employee_id in request body"
            )
        
        response = await controller.update_house_property_component(
            request, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update house property component: {str(e)}"
        )


@router.put("/records/employee/{employee_id}/capital-gains",
            response_model=ComponentUpdateResponse,
            status_code=status.HTTP_200_OK,
            summary="Update capital gains component individually",
            description="Update capital gains income component for a specific employee and tax year")
async def update_capital_gains_component(
    employee_id: str,
    request: UpdateCapitalGainsComponentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComponentUpdateResponse:
    """Update capital gains component individually."""
    
    try:
        # Ensure employee_id in path matches request
        if request.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID in path must match employee_id in request body"
            )
        
        response = await controller.update_capital_gains_component(
            request, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update capital gains component: {str(e)}"
        )


@router.put("/records/employee/{employee_id}/retirement-benefits",
            response_model=ComponentUpdateResponse,
            status_code=status.HTTP_200_OK,
            summary="Update retirement benefits component individually",
            description="Update retirement benefits component for a specific employee and tax year")
async def update_retirement_benefits_component(
    employee_id: str,
    request: UpdateRetirementBenefitsComponentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComponentUpdateResponse:
    """Update retirement benefits component individually."""
    
    try:
        # Ensure employee_id in path matches request
        if request.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID in path must match employee_id in request body"
            )
        
        response = await controller.update_retirement_benefits_component(
            request, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update retirement benefits component: {str(e)}"
        )


@router.put("/records/employee/{employee_id}/other-income",
            response_model=ComponentUpdateResponse,
            status_code=status.HTTP_200_OK,
            summary="Update other income component individually",
            description="Update other income component for a specific employee and tax year")
async def update_other_income_component(
    employee_id: str,
    request: UpdateOtherIncomeComponentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComponentUpdateResponse:
    """Update other income component individually."""
    
    try:
        # Ensure employee_id in path matches request
        if request.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID in path must match employee_id in request body"
            )
        
        response = await controller.update_other_income_component(
            request, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update other income component: {str(e)}"
        )


@router.put("/records/employee/{employee_id}/monthly-payroll",
            response_model=ComponentUpdateResponse,
            status_code=status.HTTP_200_OK,
            summary="Update monthly payroll component individually",
            description="Update monthly payroll component for a specific employee and tax year")
async def update_monthly_payroll_component(
    employee_id: str,
    request: UpdateMonthlyPayrollComponentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComponentUpdateResponse:
    """Update monthly payroll component individually."""
    
    try:
        # Ensure employee_id in path matches request
        if request.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID in path must match employee_id in request body"
            )
        
        response = await controller.update_monthly_payroll_component(
            request, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update monthly payroll component: {str(e)}"
        )


@router.put("/records/employee/{employee_id}/regime",
            response_model=ComponentUpdateResponse,
            status_code=status.HTTP_200_OK,
            summary="Update tax regime component individually",
            description="Update tax regime and age for a specific employee and tax year")
async def update_regime_component(
    employee_id: str,
    request: UpdateRegimeComponentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComponentUpdateResponse:
    """Update tax regime component individually."""
    
    try:
        # Ensure employee_id in path matches request
        if request.employee_id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID in path must match employee_id in request body"
            )
        
        response = await controller.update_regime_component(
            request, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update regime component: {str(e)}"
        )


# =============================================================================
# COMPONENT RETRIEVAL ENDPOINTS
# =============================================================================

@router.get("/records/employee/{employee_id}/component/{component_type}",
            response_model=ComponentResponse,
            summary="Get specific component from taxation record",
            description="Get a specific component (salary, perquisites, deductions, etc.) from taxation record")
async def get_component(
    employee_id: str,
    component_type: str,
    tax_year: str = Query(..., description="Tax year (e.g., '2024-25')"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComponentResponse:
    """Get a specific component from taxation record."""
    
    try:
        response = await controller.get_component(
            employee_id, tax_year, component_type, current_user.hostname
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get component {component_type}: {str(e)}"
        )


# @router.get("/records/employee/{employee_id}/status",
#             response_model=TaxationRecordStatusResponse,
#             summary="Get taxation record status",
#             description="Get status of all components in a taxation record")
# async def get_taxation_record_status(
#     employee_id: str,
#     tax_year: str = Query(..., description="Tax year (e.g., '2024-25')"),
#     current_user: CurrentUser = Depends(get_current_user),
#     controller: UnifiedTaxationController = Depends(get_taxation_controller)
# ) -> TaxationRecordStatusResponse:
#     """Get status of all components in a taxation record."""
    
#     try:
#         response = await controller.get_taxation_record_status(
#             employee_id, tax_year, current_user.hostname
#         )
#         return response
        
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=str(e)
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to get taxation record status: {str(e)}"
#         )


# =============================================================================
# EMPLOYEE SELECTION ENDPOINTS
# =============================================================================

@router.get("/employees/selection",
            response_model=EmployeeSelectionResponse,
            summary="Get employees for taxation selection",
            description="Get list of employees with tax information for admin selection interface")
async def get_employees_for_selection(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(20, description="Maximum number of records to return", le=100),
    search: Optional[str] = Query(None, description="Search term for employee name or email"),
    department: Optional[str] = Query(None, description="Filter by department"),
    role: Optional[str] = Query(None, description="Filter by role"),
    employee_status: Optional[str] = Query(None, description="Filter by employee status"),
    has_tax_record: Optional[bool] = Query(None, description="Filter by tax record availability"),
    tax_year: Optional[str] = Query(None, description="Filter by tax year"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> EmployeeSelectionResponse:
    """Get list of employees with tax information for admin selection interface."""
    try:
        logger.info(
            f"Fetching employees for selection. Filters: "
            f"search='{search}', dept='{department}', role='{role}', "
            f"status='{employee_status}', has_tax_record={has_tax_record}, "
            f"tax_year='{tax_year}', skip={skip}, limit={limit}"
        )
        
        query = EmployeeSelectionQuery(
            skip=skip,
            limit=limit,
            search=search,
            department=department,
            role=role,
            status=employee_status,
            has_tax_record=has_tax_record,
            tax_year=tax_year
        )
        
        result = await controller.get_employees_for_selection(
            query=query,
            current_user=current_user
        )
        
        logger.debug(
            f"Retrieved {len(result.employees)} employees. "
            f"Total count: {result.total}, "
            f"Filtered count: {result.total}"
        )
        return result
        
    except ValueError as e:
        logger.warning(f"Invalid input parameters: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to get employees for selection: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve employees list: {str(e)}"
        )


# =============================================================================
# INFORMATION AND UTILITY ENDPOINTS
# =============================================================================

@router.get("/tax-regimes/comparison",
            response_model=Dict[str, Any],
            summary="Compare tax regimes",
            description="Get comparison between old and new tax regimes")
async def compare_tax_regimes() -> Dict[str, Any]:
    """Compare old vs new tax regimes."""
    
    return {
        "regime_comparison": {
            "old_regime": {
                "description": "Traditional tax regime with deductions",
                "deductions_available": True,
                "exemptions_available": True,
                "perquisites_taxable": True,
                "standard_deduction": 50000,
                "popular_deductions": ["80C", "80D", "80G", "80E", "80TTA"]
            },
            "new_regime": {
                "description": "Simplified tax regime with lower rates",
                "deductions_available": False,
                "exemptions_limited": True,
                "perquisites_taxable": False,
                "standard_deduction": 50000,
                "limited_deductions": ["80CCD(2)", "80JJAA"]
            }
        },
        "tax_slabs_2024_25": {
            "old_regime": [
                {"range": "0 - 2,50,000", "rate": "0%"},
                {"range": "2,50,001 - 5,00,000", "rate": "5%"},
                {"range": "5,00,001 - 10,00,000", "rate": "20%"},
                {"range": "Above 10,00,000", "rate": "30%"}
            ],
            "new_regime": [
                {"range": "0 - 3,00,000", "rate": "0%"},
                {"range": "3,00,001 - 6,00,000", "rate": "5%"},
                {"range": "6,00,001 - 9,00,000", "rate": "10%"},
                {"range": "9,00,001 - 12,00,000", "rate": "15%"},
                {"range": "12,00,001 - 15,00,000", "rate": "20%"},
                {"range": "Above 15,00,000", "rate": "30%"}
            ]
        },
        "recommendation": "Choose regime based on total deductions available and income level"
    }


@router.get("/perquisites/types",
            response_model=Dict[str, Any],
            summary="Get perquisites types",
            description="Get list of all available perquisite types")
async def get_perquisites_types() -> Dict[str, Any]:
    """Get information about all perquisite types."""
    
    return {
        "perquisite_types": {
            "core_perquisites": {
                "accommodation": {
                    "description": "Accommodation provided by employer",
                    "types": ["Government", "Employer-Owned", "Employer-Leased", "Hotel"],
                    "city_categories": ["Above 40 lakhs", "Between 15-40 lakhs", "Below 15 lakhs"]
                },
                "car": {
                    "description": "Car provided by employer",
                    "usage_types": ["Personal", "Business", "Mixed"],
                    "engine_capacity_matters": True
                }
            },
            "medical_travel": {
                "lta": {
                    "description": "Leave Travel Allowance",
                    "exemption_conditions": "Travel within India, public transport"
                }
            },
            "financial_perquisites": {
                "interest_free_loan": {
                    "description": "Interest-free or concessional loans",
                    "sbi_rate_applicable": True
                },
                "esop": {
                    "description": "Employee Stock Option Plan benefits",
                    "taxation_on_exercise": True
                }
            }
        },
        "applicability": {
            "old_regime": "All perquisites are taxable in old tax regime",
            "new_regime": "Perquisites generally not taxable in new tax regime"
        }
    }


@router.get("/capital-gains/rates",
            response_model=Dict[str, Any],
            summary="Get capital gains tax rates",
            description="Get current capital gains tax rates")
async def get_capital_gains_rates() -> Dict[str, Any]:
    """Get capital gains tax rates information."""
    
    return {
        "short_term_capital_gains": {
            "equity_with_stt": {"rate": "15%", "description": "STCG on equity shares/equity MF with STT"},
            "other_assets": {"rate": "Slab rates", "description": "STCG on other assets added to income"}
        },
        "long_term_capital_gains": {
            "equity_with_stt": {"rate": "10%", "description": "LTCG on equity shares/equity MF with STT", "exemption": "Up to ₹1 lakh per year"},
            "other_assets": {"rate": "20%", "description": "LTCG on other assets with indexation benefit"}
        },
        "holding_periods": {
            "equity_shares": "More than 12 months for LTCG",
            "debt_instruments": "More than 36 months for LTCG",
            "real_estate": "More than 24 months for LTCG"
        }
    }


@router.get("/retirement-benefits/info",
            response_model=Dict[str, Any],
            summary="Get retirement benefits information",
            description="Get information about retirement benefits taxation")
async def get_retirement_benefits_info() -> Dict[str, Any]:
    """Get retirement benefits taxation information."""
    
    return {
        "retirement_benefits": {
            "leave_encashment": {
                "description": "Leave encashment on retirement/resignation",
                "exemption_govt": "No upper limit for government employees",
                "exemption_private": "Least of actual, 10 months average salary, or cash equivalent of unavailed leave"
            },
            "gratuity": {
                "description": "Gratuity payment on retirement",
                "exemption_govt": "No upper limit for government employees",
                "exemption_private": "₹20 lakhs or actual gratuity, whichever is less"
            },
            "vrs": {
                "description": "Voluntary Retirement Scheme compensation",
                "exemption": "₹5 lakhs or 3 months salary × remaining service years, whichever is less"
            }
        }
    }


@router.get("/tax-years",
            response_model=List[Dict[str, str]],
            summary="Get available tax years",
            description="Get list of available tax years for selection")
async def get_available_tax_years() -> List[Dict[str, str]]:
    """Get available tax years."""
    
    from app.domain.value_objects.tax_year import TaxYear
    from datetime import date
    
    current_year = date.today().year
    tax_years = []
    
    # Generate last 5 years and next 2 years
    for year in range(current_year - 5, current_year + 3):
        try:
            tax_year = TaxYear(year, year + 1)
            tax_years.append({
                "value": str(tax_year),
                "display_name": tax_year.get_display_name(),
                "assessment_year": tax_year.get_assessment_year(),
                "is_current": tax_year.is_current_year()
            })
        except ValueError:
            continue
    
    return tax_years


@router.get("/health",
            summary="Health check for taxation service",
            description="Check if taxation service is healthy")
async def health_check() -> Dict[str, str]:
    """Check if taxation service and its dependencies are healthy."""
    try:
        logger.debug("Starting taxation service health check")
        
        # Check database connection
        from app.config.dependency_container import get_dependency_container
        container = get_dependency_container()
        repository = container.get_taxation_repository()
        await repository.check_connection()
        
        # Check calculation service
        calculation_service = container.get_tax_calculation_service()
        calculation_service.validate_configuration()
        
        logger.info("Taxation service health check passed")
        return {
            "status": "healthy",
            "message": "Taxation service is running normally",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Taxation service health check failed: {str(e)}", exc_info=True)
        return {
            "status": "unhealthy",
            "message": f"Taxation service health check failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }


# =============================================================================
# MONTHLY TAX COMPUTATION - NEW SALARY PACKAGE BASED ENDPOINTS  
# =============================================================================

@router.get("/monthly-tax/employee/{employee_id}",
            response_model=Dict[str, Any],
            status_code=status.HTTP_200_OK,
            summary="Compute monthly tax for employee",
            description="Compute tax for employee for the current month and year")
async def compute_monthly_tax(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> Dict[str, Any]:
    """
    Compute monthly tax for an employee for the current month and year.
    
    Convenience endpoint that automatically uses the current month and year.
    """
    
    try:
        result = await controller.compute_monthly_tax(employee_id, current_user.hostname)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute monthly tax: {str(e)}"
        )

@router.get("/monthly-tax/current/{employee_id}",
            response_model=Dict[str, Any],
            status_code=status.HTTP_200_OK,
            summary="Compute current month tax for employee",
            description="Compute tax for employee for the current month and year")
async def compute_current_month_tax(
    employee_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> Dict[str, Any]:
    """
    Compute monthly tax for an employee for the current month and year.
    
    Convenience endpoint that automatically uses the current month and year.
    """
    
    try:
        from datetime import datetime
        now = datetime.now()
        
        result = await controller.compute_monthly_tax(
            employee_id, now.month, now.year, current_user.hostname
        )
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute current month tax: {str(e)}"
        )

@router.get("/export/salary-package/{employee_id}",
            status_code=status.HTTP_200_OK,
            summary="Export comprehensive salary package to Excel (multiple sheets)",
            description="Export complete salary package with all components to Excel with multiple sheets")
async def export_salary_package_to_excel(
    employee_id: str,
    tax_year: Optional[str] = Query(None, description="Tax year (e.g., '2025-26')"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> Response:
    """
    Export comprehensive salary package data to Excel format with multiple sheets.
    """
    try:
        excel_content = await controller.export_salary_package_to_excel(
            employee_id, tax_year, current_user.hostname
        )
        
        # Generate filename
        year_suffix = f"_{tax_year}" if tax_year else ""
        filename = f"salary_package_{employee_id}{year_suffix}.xlsx"
        
        return Response(
            content=excel_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        logger.error(f"Error exporting salary package to Excel: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export salary package: {str(e)}"
        )

@router.get("/export/salary-package-single/{employee_id}",
            status_code=status.HTTP_200_OK,
            summary="Export comprehensive salary package to Excel (single sheet)",
            description="Export complete salary package with all components to Excel in a single sheet")
async def export_salary_package_single_sheet(
    employee_id: str,
    tax_year: Optional[str] = Query(None, description="Tax year (e.g., '2025-26')"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> Response:
    """
    Export comprehensive salary package data to Excel format in a single sheet.
    """
    try:
        excel_content = await controller.export_salary_package_single_sheet(
            employee_id, tax_year, current_user.hostname
        )
        
        # Generate filename
        year_suffix = f"_{tax_year}" if tax_year else ""
        filename = f"salary_package_single_{employee_id}{year_suffix}.xlsx"
        
        return Response(
            content=excel_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        logger.error(f"Error exporting salary package to single Excel sheet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export salary package to single sheet: {str(e)}"
        )


# =============================================================================
# MONTHLY SALARY COMPUTATION ENDPOINTS
# =============================================================================

@router.post("/monthly-salary/compute",
            response_model=MonthlySalaryResponseDTO,
            status_code=status.HTTP_200_OK,
            summary="Compute monthly salary for employee",
            description="Compute monthly salary with all components and deductions")
async def compute_monthly_salary(
    request: MonthlySalaryComputeRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> MonthlySalaryResponseDTO:
    """
    Compute monthly salary for an employee.
    
    This endpoint:
    1. Takes monthly salary computation request with month, year, arrears, etc.
    2. Uses the MonthlySalary entity to compute salary components
    3. Calculates deductions and tax liability
    4. Returns detailed monthly salary breakdown
    
    Args:
        request: Monthly salary computation request
        current_user: Current authenticated user
        
    Returns:
        MonthlySalaryResponseDTO: Computed monthly salary details
        
    Raises:
        HTTPException: If computation fails
    """
    
    try:
        logger.info(f"Computing monthly salary for employee {request.employee_id}")
        logger.info(f"Month: {request.month}, Year: {request.year}, Tax Year: {request.tax_year}")
        
        result = await controller.compute_monthly_salary(request, current_user.hostname)
        
        logger.info(f"Successfully computed monthly salary for employee {request.employee_id}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error in monthly salary computation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except RuntimeError as e:
        logger.error(f"Runtime error in monthly salary computation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in monthly salary computation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compute monthly salary: {str(e)}"
        )

