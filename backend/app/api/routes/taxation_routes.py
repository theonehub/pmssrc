"""
Comprehensive Taxation API Routes
Production-ready REST API endpoints for all taxation operations and income types
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from datetime import datetime

from app.auth.auth_dependencies import get_current_user, CurrentUser
from app.application.dto.taxation_dto import (
    # Comprehensive DTOs
    ComprehensiveTaxInputDTO,
    PeriodicTaxCalculationResponseDTO,
    ComprehensiveTaxOutputDTO,
    PerquisitesDTO,
    HousePropertyIncomeDTO,
    MultipleHousePropertiesDTO,
    CapitalGainsIncomeDTO,
    RetirementBenefitsDTO,
    OtherIncomeDTO,
    AnnualPayrollWithLWPDTO,
    
    # Scenario DTOs
    ScenarioComparisonRequestDTO,
    ScenarioComparisonResponseDTO,
    MidYearJoinerDTO,
    MidYearIncrementDTO,
    
    # Record management DTOs
    CreateTaxationRecordRequest,
    CreateTaxationRecordResponse,
    TaxationRecordSummaryDTO,
    TaxationRecordListResponse,
    TaxationRecordQuery,
    UpdateResponse,
    
    # Employee Selection DTOs
    EmployeeSelectionQuery,
    EmployeeSelectionResponse
)
from app.api.controllers.taxation_controller import UnifiedTaxationController
from app.config.dependency_container import (
    get_comprehensive_taxation_controller,
    get_taxation_controller
)
from app.domain.exceptions.taxation_exceptions import (
    TaxationRecordNotFoundError,
    TaxationValidationError,
    TaxCalculationError,
    FinalizedRecordError,
    DuplicateTaxationRecordError
)


router = APIRouter(prefix="/api/v2/taxation", tags=["taxation"])


# =============================================================================
# COMPREHENSIVE TAX CALCULATION - MAIN ENDPOINTS
# =============================================================================

@router.post("/calculate-comprehensive",
             response_model=PeriodicTaxCalculationResponseDTO,
             status_code=status.HTTP_200_OK,
             summary="Calculate comprehensive tax",
             description="Calculate tax including all income sources and components")
async def calculate_comprehensive_tax(
    request: ComprehensiveTaxInputDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_comprehensive_taxation_controller)
) -> PeriodicTaxCalculationResponseDTO:
    """Calculate comprehensive tax including all income sources."""
    
    try:
        response = await controller.calculate_comprehensive_tax(
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
            detail=f"Failed to calculate comprehensive tax: {str(e)}"
        )


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
    controller: UnifiedTaxationController = Depends(get_comprehensive_taxation_controller)
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
    house_property: HousePropertyIncomeDTO,
    regime_type: str = Query(..., description="Tax regime: 'old' or 'new'"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_comprehensive_taxation_controller)
) -> Dict[str, Any]:
    """Calculate house property income tax."""
    
    try:
        response = await controller.calculate_house_property_only(
            house_property, regime_type, current_user.hostname
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
    controller: UnifiedTaxationController = Depends(get_comprehensive_taxation_controller)
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
    controller: UnifiedTaxationController = Depends(get_comprehensive_taxation_controller)
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


@router.post("/payroll/calculate",
             response_model=Dict[str, Any],
             status_code=status.HTTP_200_OK,
             summary="Calculate payroll tax with LWP",
             description="Calculate monthly payroll tax with Leave Without Pay considerations")
async def calculate_payroll_tax(
    payroll: AnnualPayrollWithLWPDTO,
    regime_type: str = Query(..., description="Tax regime: 'old' or 'new'"),
    age: int = Query(..., description="Employee age"),
    section_80c: float = Query(0, description="Section 80C investments"),
    section_80d: float = Query(0, description="Section 80D health insurance"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_comprehensive_taxation_controller)
) -> Dict[str, Any]:
    """Calculate payroll tax with LWP considerations."""
    
    try:
        deductions_data = {
            "section_80c": section_80c,
            "section_80d": section_80d
        }
        
        response = await controller.calculate_payroll_tax(
            payroll, deductions_data, regime_type, age, current_user.hostname
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
            detail=f"Failed to calculate payroll tax: {str(e)}"
        )


# =============================================================================
# SCENARIO CALCULATION ENDPOINTS
# =============================================================================

@router.post("/mid-year/joiner",
             response_model=PeriodicTaxCalculationResponseDTO,
             status_code=status.HTTP_200_OK,
             summary="Calculate mid-year joiner tax",
             description="Calculate tax for mid-year joiner scenario")
async def calculate_mid_year_joiner(
    request: MidYearJoinerDTO,
    tax_year: str = Query(..., description="Tax year (e.g., '2024-25')"),
    regime_type: str = Query(..., description="Tax regime: 'old' or 'new'"),
    age: int = Query(..., description="Employee age"),
    section_80c: float = Query(0, description="Section 80C investments"),
    section_80d: float = Query(0, description="Section 80D health insurance"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_comprehensive_taxation_controller)
) -> PeriodicTaxCalculationResponseDTO:
    """Calculate tax for mid-year joiner scenario."""
    
    try:
        # Convert to comprehensive input and calculate
        comprehensive_request = _convert_mid_year_joiner_to_comprehensive(
            request, tax_year, regime_type, age, section_80c, section_80d
        )
        
        response = await controller.calculate_comprehensive_tax(
            comprehensive_request, current_user.hostname
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
            detail=f"Failed to calculate mid-year joiner tax: {str(e)}"
        )


@router.post("/mid-year/increment",
             response_model=PeriodicTaxCalculationResponseDTO,
             status_code=status.HTTP_200_OK,
             summary="Calculate mid-year increment tax",
             description="Calculate tax for mid-year increment scenario")
async def calculate_mid_year_increment(
    request: MidYearIncrementDTO,
    tax_year: str = Query(..., description="Tax year (e.g., '2024-25')"),
    regime_type: str = Query(..., description="Tax regime: 'old' or 'new'"),
    age: int = Query(..., description="Employee age"),
    section_80c: float = Query(0, description="Section 80C investments"),
    section_80d: float = Query(0, description="Section 80D health insurance"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_comprehensive_taxation_controller)
) -> PeriodicTaxCalculationResponseDTO:
    """Calculate tax for mid-year increment scenario."""
    
    try:
        # Convert to comprehensive input and calculate
        comprehensive_request = _convert_mid_year_increment_to_comprehensive(
            request, tax_year, regime_type, age, section_80c, section_80d
        )
        
        response = await controller.calculate_comprehensive_tax(
            comprehensive_request, current_user.hostname
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
            detail=f"Failed to calculate mid-year increment tax: {str(e)}"
        )


@router.post("/scenarios/compare",
             response_model=ScenarioComparisonResponseDTO,
             status_code=status.HTTP_200_OK,
             summary="Compare tax scenarios",
             description="Compare different tax scenarios")
async def compare_scenarios(
    request: ScenarioComparisonRequestDTO,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_comprehensive_taxation_controller)
) -> ScenarioComparisonResponseDTO:
    """Compare different tax scenarios."""
    
    try:
        # Calculate base scenario
        base_result = await controller.calculate_comprehensive_tax(
            request.base_request, current_user.hostname
        )
        
        # Build comparison response
        return ScenarioComparisonResponseDTO(
            base_scenario=base_result,
            comparison_scenarios=[],
            recommendations=[
                "Consider optimizing deductions based on regime",
                "Review salary structure for tax efficiency",
                "Plan investments for tax benefits"
            ],
            summary={
                "base_tax_liability": base_result.total_tax_liability,
                "regime_used": base_result.regime_used,
                "effective_rate": base_result.effective_tax_rate
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare scenarios: {str(e)}"
        )


# =============================================================================
# RECORD MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/records", 
             response_model=CreateTaxationRecordResponse,
             status_code=status.HTTP_201_CREATED,
             summary="Create new taxation record",
             description="Create a new taxation record for a user and tax year")
async def create_taxation_record(
    request: CreateTaxationRecordRequest,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> CreateTaxationRecordResponse:
    """Create new taxation record."""
    
    try:
        response = await controller.create_taxation_record(
            request, current_user.hostname
        )
        return response
        
    except DuplicateTaxationRecordError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except TaxationValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create taxation record: {str(e)}"
        )


@router.get("/records",
            response_model=TaxationRecordListResponse,
            summary="List taxation records",
            description="Get list of taxation records with optional filters")
async def list_taxation_records(
    query: TaxationRecordQuery = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> TaxationRecordListResponse:
    """List taxation records with filtering and pagination."""
    
    try:
        response = await controller.list_taxation_records(
            query, current_user.hostname
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list taxation records: {str(e)}"
        )

@router.get("/records/employee/{employee_id}",
            response_model=ComprehensiveTaxOutputDTO,
            summary="Get comprehensive taxation record by employee ID",
            description="Get comprehensive taxation record by employee ID and optional tax year with computed values")
async def get_taxation_record_by_employee(
    employee_id: str,
    tax_year: Optional[str] = Query(None, description="Tax year (e.g., '2024-25')"),
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> ComprehensiveTaxOutputDTO:
    """Get comprehensive taxation record by employee ID and optional tax year."""
    
    try:
        response = await controller.get_taxation_record_by_employee(
            employee_id, current_user.hostname, tax_year
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get comprehensive taxation record: {str(e)}"
        )


@router.get("/records/{taxation_id}",
            response_model=TaxationRecordSummaryDTO,
            summary="Get taxation record",
            description="Get taxation record by ID")
async def get_taxation_record(
    taxation_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    controller: UnifiedTaxationController = Depends(get_taxation_controller)
) -> TaxationRecordSummaryDTO:
    """Get taxation record by ID."""
    
    try:
        response = await controller.get_taxation_record(
            taxation_id, current_user.hostname
        )
        return response
        
    except TaxationRecordNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Taxation record not found: {taxation_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get taxation record: {str(e)}"
        )


# =============================================================================
# EMPLOYEE SELECTION ENDPOINTS
# =============================================================================

@router.get("/employee-selection",
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
    """Get employees for taxation selection with filtering and pagination."""
    
    try:
        # Create query object
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
        
        response = await controller.get_employees_for_selection(
            query, current_user
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get employees for selection: {str(e)}"
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
                "medical_reimbursement": {
                    "description": "Medical expenses reimbursed by employer",
                    "overseas_treatment_applicable": True
                },
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


@router.get("/optimization-strategies",
            response_model=Dict[str, Any],
            summary="Get tax optimization strategies",
            description="Get comprehensive tax optimization strategies")
async def get_optimization_strategies() -> Dict[str, Any]:
    """Get tax optimization strategies."""
    
    return {
        "general_strategies": {
            "regime_selection": {
                "strategy": "Choose optimal tax regime based on deductions",
                "considerations": ["Total deduction amount", "Perquisites value", "Income level", "Investment preferences"]
            },
            "income_structuring": {
                "strategy": "Optimize income structure for tax efficiency",
                "methods": ["Salary vs perquisites balance", "Bonus timing optimization", "Leave encashment planning"]
            },
            "investment_planning": {
                "strategy": "Structure investments for maximum tax benefit",
                "approaches": ["Tax-saving investments (80C, 80D, etc.)", "Capital gains optimization", "Tax-efficient mutual funds"]
            }
        },
        "regime_specific_strategies": {
            "old_regime": {
                "focus": "Maximize deductions and exemptions",
                "strategies": ["Utilize full Section 80C limit", "Optimize health insurance under 80D", "Plan charitable donations"]
            },
            "new_regime": {
                "focus": "Benefit from lower tax rates",
                "strategies": ["Focus on salary optimization", "Minimize taxable perquisites", "Plan capital gains efficiently"]
            }
        }
    }


@router.get("/health",
            summary="Health check for taxation service",
            description="Check if taxation service is healthy")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for taxation service."""
    return {
        "status": "healthy",
        "service": "comprehensive_taxation",
        "version": "2.0.0",
        "features": [
            "Comprehensive tax calculation",
            "All income types supported",
            "Perquisites calculation", 
            "House property income",
            "Capital gains",
            "Retirement benefits",
            "Monthly payroll with LWP",
            "Mid-year scenarios",
            "Scenario comparison",
            "Tax optimization"
        ],
        "timestamp": str(datetime.utcnow())
    }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _convert_mid_year_joiner_to_comprehensive(
    request: MidYearJoinerDTO, 
    tax_year: str, 
    regime_type: str, 
    age: int, 
    section_80c: float, 
    section_80d: float
) -> ComprehensiveTaxInputDTO:
    """Convert mid-year joiner request to comprehensive input."""
    
    from app.application.dto.taxation_dto import SalaryIncomeDTO, TaxDeductionsDTO
    
    salary_dto = SalaryIncomeDTO(
        basic_salary=request.salary_details.basic_salary,
        dearness_allowance=request.salary_details.dearness_allowance,
        hra_received=request.salary_details.hra_received,
        hra_city_type=request.salary_details.hra_city_type,
        actual_rent_paid=request.salary_details.actual_rent_paid,
        bonus=request.salary_details.bonus,
        commission=request.salary_details.commission,
        special_allowance=request.salary_details.special_allowance,
        other_allowances=request.salary_details.other_allowances,
        lta_received=request.salary_details.lta_received,
        medical_allowance=request.salary_details.medical_allowance,
        conveyance_allowance=request.salary_details.conveyance_allowance
    )
    
    deductions_dto = TaxDeductionsDTO(
        section_80c_investments=section_80c,
        section_80d_health_insurance=section_80d
    )
    
    return ComprehensiveTaxInputDTO(
        salary_income=salary_dto,
        deductions=deductions_dto,
        regime_type=regime_type,
        age=age,
        tax_year=tax_year
    )


def _convert_mid_year_increment_to_comprehensive(
    request: MidYearIncrementDTO, 
    tax_year: str, 
    regime_type: str, 
    age: int, 
    section_80c: float, 
    section_80d: float
) -> ComprehensiveTaxInputDTO:
    """Convert mid-year increment request to comprehensive input."""
    
    from app.application.dto.taxation_dto import SalaryIncomeDTO, TaxDeductionsDTO
    
    # Use post-increment salary for calculation
    salary_dto = SalaryIncomeDTO(
        basic_salary=request.post_increment_salary.basic_salary,
        dearness_allowance=request.post_increment_salary.dearness_allowance,
        hra_received=request.post_increment_salary.hra_received,
        hra_city_type=request.post_increment_salary.hra_city_type,
        actual_rent_paid=request.post_increment_salary.actual_rent_paid,
        special_allowance=request.post_increment_salary.special_allowance,
        other_allowances=request.post_increment_salary.other_allowances,
        bonus=request.post_increment_salary.bonus,
        commission=request.post_increment_salary.commission,
        lta_received=request.post_increment_salary.lta_received,
        medical_allowance=request.post_increment_salary.medical_allowance,
        conveyance_allowance=request.post_increment_salary.conveyance_allowance
    )
    
    deductions_dto = TaxDeductionsDTO(
        section_80c_investments=section_80c,
        section_80d_health_insurance=section_80d
    )
    
    return ComprehensiveTaxInputDTO(
        salary_income=salary_dto,
        deductions=deductions_dto,
        regime_type=regime_type,
        age=age,
        tax_year=tax_year
    ) 