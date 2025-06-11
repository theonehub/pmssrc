"""
Comprehensive Taxation API Routes
Production-ready REST API endpoints for all taxation operations and income types
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from datetime import datetime

from app.auth.auth_dependencies import get_current_user, CurrentUser
from app.application.dto.taxation_dto import (
    # Comprehensive DTOs
    ComprehensiveTaxInputDTO,
    PeriodicTaxCalculationResponseDTO,
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
    UpdateResponse
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


router = APIRouter(prefix="/api/v1/taxation", tags=["taxation"])


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
            request, current_user.organization_id
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
            perquisites, regime_type, current_user.organization_id
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
            house_property, regime_type, current_user.organization_id
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
            capital_gains, regime_type, current_user.organization_id
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
            retirement_benefits, regime_type, current_user.organization_id
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
        response = await controller.calculate_payroll_tax(
            payroll, regime_type, age, section_80c, section_80d, current_user.organization_id
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
# SCENARIO CALCULATIONS
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
        # Convert to comprehensive input
        comprehensive_input = _convert_mid_year_joiner_to_comprehensive(
            request, tax_year, regime_type, age, section_80c, section_80d
        )
        
        # Calculate using comprehensive endpoint
        response = await controller.calculate_comprehensive_tax(
            comprehensive_input, current_user.organization_id
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
        # Convert to comprehensive input
        comprehensive_input = _convert_mid_year_increment_to_comprehensive(
            request, tax_year, regime_type, age, section_80c, section_80d
        )
        
        # Calculate using comprehensive endpoint
        response = await controller.calculate_comprehensive_tax(
            comprehensive_input, current_user.organization_id
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
        response = await controller.compare_scenarios(
            request, current_user.organization_id
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
            detail=f"Failed to compare scenarios: {str(e)}"
        )


# =============================================================================
# TAXATION RECORD MANAGEMENT
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
    """Create a new taxation record."""
    
    try:
        response = await controller.create_taxation_record(
            request, current_user.organization_id
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
    """List taxation records with filters."""
    
    try:
        response = await controller.list_taxation_records(
            query, current_user.organization_id
        )
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list taxation records: {str(e)}"
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
            taxation_id, current_user.organization_id
        )
        return response
        
    except TaxationRecordNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get taxation record: {str(e)}"
        )


# =============================================================================
# INFORMATION ENDPOINTS
# =============================================================================

@router.get("/tax-regimes/comparison",
            response_model=Dict[str, Any],
            summary="Compare tax regimes",
            description="Get comparison between old and new tax regimes")
async def compare_tax_regimes() -> Dict[str, Any]:
    """Get comparison between old and new tax regimes."""
    
    try:
        return {
            "old_regime": {
                "name": "Old Tax Regime",
                "description": "Traditional tax regime with all deductions and exemptions",
                "key_features": [
                    "All standard deductions available",
                    "Section 80C deductions up to ₹1.5L",
                    "HRA exemption",
                    "LTA benefits",
                    "Medical insurance deductions",
                    "Home loan interest deductions"
                ],
                "suitable_for": [
                    "People with high investments in tax-saving instruments",
                    "Those claiming HRA benefits",
                    "People with home loans",
                    "Those with high medical insurance premiums"
                ]
            },
            "new_regime": {
                "name": "New Tax Regime",
                "description": "Simplified tax regime with lower rates but fewer deductions",
                "key_features": [
                    "Lower tax rates",
                    "No standard deduction",
                    "No Section 80C benefits",
                    "No HRA exemption",
                    "No LTA benefits",
                    "Limited deductions"
                ],
                "suitable_for": [
                    "People with minimal investments",
                    "Those not claiming HRA",
                    "People without home loans",
                    "Those preferring simpler tax filing"
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax regime comparison: {str(e)}"
        )


@router.get("/perquisites/types",
            response_model=Dict[str, Any],
            summary="Get perquisites types",
            description="Get list of all available perquisite types")
async def get_perquisites_types() -> Dict[str, Any]:
    """Get list of all available perquisite types."""
    
    try:
        return {
            "perquisites": [
                {
                    "type": "rent_free_accommodation",
                    "name": "Rent Free Accommodation",
                    "description": "Company provided accommodation without rent",
                    "taxable_value": "Based on salary and city classification"
                },
                {
                    "type": "car_with_driver",
                    "name": "Car with Driver",
                    "description": "Company provided car with driver",
                    "taxable_value": "Based on car value and maintenance costs"
                },
                {
                    "type": "car_without_driver",
                    "name": "Car without Driver",
                    "description": "Company provided car without driver",
                    "taxable_value": "Based on car value and maintenance costs"
                },
                {
                    "type": "education_allowance",
                    "name": "Education Allowance",
                    "description": "Allowance for children's education",
                    "taxable_value": "Amount exceeding ₹100 per month per child"
                },
                {
                    "type": "medical_reimbursement",
                    "name": "Medical Reimbursement",
                    "description": "Reimbursement of medical expenses",
                    "taxable_value": "Amount exceeding ₹15,000 per year"
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get perquisites types: {str(e)}"
        )


@router.get("/capital-gains/rates",
            response_model=Dict[str, Any],
            summary="Get capital gains tax rates",
            description="Get current capital gains tax rates")
async def get_capital_gains_rates() -> Dict[str, Any]:
    """Get current capital gains tax rates."""
    
    try:
        return {
            "short_term": {
                "equity": {
                    "holding_period": "Less than 12 months",
                    "tax_rate": 15,
                    "cess": 4,
                    "total_rate": 15.6
                },
                "non_equity": {
                    "holding_period": "Less than 36 months",
                    "tax_rate": "As per income tax slab",
                    "cess": 4,
                    "total_rate": "Slab rate + 4% cess"
                }
            },
            "long_term": {
                "equity": {
                    "holding_period": "More than 12 months",
                    "tax_rate": 10,
                    "cess": 4,
                    "total_rate": 10.4,
                    "exemption_limit": 100000
                },
                "non_equity": {
                    "holding_period": "More than 36 months",
                    "tax_rate": 20,
                    "cess": 4,
                    "total_rate": 20.8,
                    "indexation": "Available"
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get capital gains rates: {str(e)}"
        )


@router.get("/retirement-benefits/info",
            response_model=Dict[str, Any],
            summary="Get retirement benefits information",
            description="Get information about retirement benefits taxation")
async def get_retirement_benefits_info() -> Dict[str, Any]:
    """Get information about retirement benefits taxation."""
    
    try:
        return {
            "gratuity": {
                "description": "Lump sum payment made by employer on retirement",
                "tax_exemption": {
                    "government_employees": "Fully exempt",
                    "private_employees": "Least of:",
                    "exemption_limits": [
                        "₹20,00,000",
                        "15 days salary × years of service",
                        "Actual gratuity received"
                    ]
                }
            },
            "leave_encashment": {
                "description": "Payment for unused leave at retirement",
                "tax_exemption": {
                    "government_employees": "Fully exempt",
                    "private_employees": "Least of:",
                    "exemption_limits": [
                        "₹3,00,000",
                        "10 months average salary",
                        "Cash equivalent of leave balance",
                        "Actual amount received"
                    ]
                }
            },
            "commuted_pension": {
                "description": "Lump sum payment in lieu of monthly pension",
                "tax_exemption": {
                    "government_employees": "Fully exempt",
                    "private_employees": "1/3rd of commuted value exempt if gratuity received, 1/2 if no gratuity"
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get retirement benefits info: {str(e)}"
        )


@router.get("/tax-years",
            response_model=List[Dict[str, str]],
            summary="Get available tax years",
            description="Get list of available tax years for selection")
async def get_available_tax_years() -> List[Dict[str, str]]:
    """Get list of available tax years for selection."""
    
    try:
        current_year = datetime.now().year
        years = []
        
        # Generate last 5 years and next 2 years
        for year in range(current_year - 5, current_year + 3):
            years.append({
                "id": f"{year}-{str(year + 1)[-2:]}",
                "name": f"FY {year}-{str(year + 1)[-2:]}"
            })
            
        return years
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tax years: {str(e)}"
        )


@router.get("/optimization-strategies",
            response_model=Dict[str, Any],
            summary="Get tax optimization strategies",
            description="Get comprehensive tax optimization strategies")
async def get_optimization_strategies() -> Dict[str, Any]:
    """Get comprehensive tax optimization strategies."""
    
    try:
        return {
            "strategies": [
                {
                    "category": "Salary Structure",
                    "strategies": [
                        {
                            "name": "HRA Optimization",
                            "description": "Maximize HRA exemption by proper rent payment and documentation",
                            "benefits": "Up to 50% of basic salary in metro cities"
                        },
                        {
                            "name": "LTA Planning",
                            "description": "Plan LTA claims across years for maximum benefit",
                            "benefits": "Tax-free travel allowance"
                        }
                    ]
                },
                {
                    "category": "Investments",
                    "strategies": [
                        {
                            "name": "Section 80C",
                            "description": "Utilize full ₹1.5L limit through various instruments",
                            "options": [
                                "EPF",
                                "ELSS",
                                "NPS",
                                "Life Insurance",
                                "Home Loan Principal"
                            ]
                        },
                        {
                            "name": "NPS Additional",
                            "description": "Additional ₹50,000 deduction under Section 80CCD(1B)",
                            "benefits": "Extra tax saving over 80C limit"
                        }
                    ]
                },
                {
                    "category": "Health & Insurance",
                    "strategies": [
                        {
                            "name": "Health Insurance",
                            "description": "Utilize Section 80D for health insurance premiums",
                            "limits": {
                                "self_family": "₹25,000",
                                "parents": "₹25,000 (₹50,000 if senior citizens)"
                            }
                        },
                        {
                            "name": "Medical Expenses",
                            "description": "Claim medical expenses for senior citizens",
                            "benefits": "Deduction up to ₹50,000 under Section 80D"
                        }
                    ]
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get optimization strategies: {str(e)}"
        )


@router.get("/health",
            summary="Health check for taxation service",
            description="Check if taxation service is healthy")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


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
    """Convert mid-year joiner request to comprehensive tax input."""
    
    # Extract months from tax year
    start_year = int(tax_year.split("-")[0])
    end_year = int(tax_year.split("-")[1])
    
    # Calculate months from joining date
    joining_date = datetime.strptime(request.joining_date, "%Y-%m-%d")
    months_from_joining = (end_year - joining_date.year) * 12 + (12 - joining_date.month + 1)
    
    # Calculate monthly salary
    monthly_salary = request.annual_salary / 12
    
    # Create monthly salary structure
    monthly_salaries = []
    for month in range(1, 13):
        if month >= joining_date.month:
            monthly_salaries.append({
                "month": month,
                "basic": monthly_salary * 0.4,  # 40% of monthly salary
                "hra": monthly_salary * 0.4,    # 40% of monthly salary
                "special_allowance": monthly_salary * 0.2  # 20% of monthly salary
            })
        else:
            monthly_salaries.append({
                "month": month,
                "basic": 0,
                "hra": 0,
                "special_allowance": 0
            })
    
    # Create comprehensive input
    return ComprehensiveTaxInputDTO(
        tax_year=tax_year,
        regime_type=regime_type,
        age=age,
        monthly_salaries=monthly_salaries,
        section_80c=section_80c,
        section_80d=section_80d,
        perquisites=request.perquisites,
        house_property_income=request.house_property_income,
        capital_gains=request.capital_gains,
        other_income=request.other_income
    )


def _convert_mid_year_increment_to_comprehensive(
    request: MidYearIncrementDTO, 
    tax_year: str, 
    regime_type: str, 
    age: int, 
    section_80c: float, 
    section_80d: float
) -> ComprehensiveTaxInputDTO:
    """Convert mid-year increment request to comprehensive tax input."""
    
    # Extract months from tax year
    start_year = int(tax_year.split("-")[0])
    end_year = int(tax_year.split("-")[1])
    
    # Calculate months from increment date
    increment_date = datetime.strptime(request.increment_date, "%Y-%m-%d")
    months_from_increment = (end_year - increment_date.year) * 12 + (12 - increment_date.month + 1)
    
    # Calculate monthly salaries
    monthly_salaries = []
    for month in range(1, 13):
        if month < increment_date.month:
            # Pre-increment salary
            monthly_salaries.append({
                "month": month,
                "basic": request.pre_increment_salary * 0.4 / 12,  # 40% of pre-increment
                "hra": request.pre_increment_salary * 0.4 / 12,    # 40% of pre-increment
                "special_allowance": request.pre_increment_salary * 0.2 / 12  # 20% of pre-increment
            })
        else:
            # Post-increment salary
            monthly_salaries.append({
                "month": month,
                "basic": request.post_increment_salary * 0.4 / 12,  # 40% of post-increment
                "hra": request.post_increment_salary * 0.4 / 12,    # 40% of post-increment
                "special_allowance": request.post_increment_salary * 0.2 / 12  # 20% of post-increment
            })
    
    # Create comprehensive input
    return ComprehensiveTaxInputDTO(
        tax_year=tax_year,
        regime_type=regime_type,
        age=age,
        monthly_salaries=monthly_salaries,
        section_80c=section_80c,
        section_80d=section_80d,
        perquisites=request.perquisites,
        house_property_income=request.house_property_income,
        capital_gains=request.capital_gains,
        other_income=request.other_income
    ) 