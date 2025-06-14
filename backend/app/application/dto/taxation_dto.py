"""
Comprehensive Taxation DTOs
Data Transfer Objects for taxation API covering all scenarios including mid-year and periodic calculations
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator


# =============================================================================
# BASIC VALUE OBJECTS
# =============================================================================

class MoneyDTO(BaseModel):
    """Money DTO for API serialization."""
    amount: Decimal = Field(..., ge=0, description="Amount in INR")
    currency: str = Field(default="INR", description="Currency code")
    
    @validator('currency')
    def validate_currency(cls, v):
        if v != "INR":
            raise ValueError("Only INR currency is supported")
        return v


class EmploymentPeriodDTO(BaseModel):
    """DTO for employment period information."""
    
    start_date: date = Field(..., description="Start date of employment period")
    end_date: Optional[date] = Field(None, description="End date of employment period (None for ongoing)")
    description: str = Field(..., description="Description of the period")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate end date is not before start date."""
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('End date cannot be before start date')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "start_date": "2024-04-01",
                "end_date": "2024-09-30",
                "description": "Pre-increment period"
            }
        }


# =============================================================================
# SALARY INCOME DTOs
# =============================================================================

class SalaryIncomeDTO(BaseModel):
    """Basic salary income DTO."""
    basic_salary: Decimal = Field(..., ge=0)
    dearness_allowance: Decimal = Field(default=0, ge=0)
    hra_received: Decimal = Field(default=0, ge=0)
    hra_city_type: str = Field(default="non_metro", description="metro or non_metro")
    actual_rent_paid: Decimal = Field(default=0, ge=0)
    special_allowance: Decimal = Field(default=0, ge=0)
    other_allowances: Decimal = Field(default=0, ge=0)
    lta_received: Decimal = Field(default=0, ge=0)
    medical_allowance: Decimal = Field(default=0, ge=0)
    conveyance_allowance: Decimal = Field(default=0, ge=0)
    
    @validator('hra_city_type')
    def validate_city_type(cls, v):
        if v not in ["metro", "non_metro"]:
            raise ValueError("City type must be 'metro' or 'non_metro'")
        return v


class PeriodicSalaryDataDTO(BaseModel):
    """DTO for salary data in a specific period."""
    
    period: EmploymentPeriodDTO
    basic_salary: Decimal = Field(..., gt=0, description="Basic salary amount")
    dearness_allowance: Decimal = Field(0, ge=0, description="Dearness allowance")
    hra_received: Decimal = Field(0, ge=0, description="HRA received")
    hra_city_type: str = Field("non_metro", description="City type for HRA calculation")
    actual_rent_paid: Decimal = Field(0, ge=0, description="Actual rent paid")
    special_allowance: Decimal = Field(0, ge=0, description="Special allowance")
    other_allowances: Decimal = Field(0, ge=0, description="Other allowances")
    lta_received: Decimal = Field(0, ge=0, description="LTA received")
    medical_allowance: Decimal = Field(0, ge=0, description="Medical allowance")
    conveyance_allowance: Decimal = Field(0, ge=0, description="Conveyance allowance")
    
    @validator('hra_city_type')
    def validate_city_type(cls, v):
        """Validate HRA city type."""
        if v not in ["metro", "non_metro"]:
            raise ValueError('HRA city type must be "metro" or "non_metro"')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "period": {
                    "start_date": "2024-04-01",
                    "end_date": "2024-09-30",
                    "description": "Pre-increment period"
                },
                "basic_salary": 600000,
                "dearness_allowance": 60000,
                "hra_received": 240000,
                "hra_city_type": "metro",
                "actual_rent_paid": 300000,
                "special_allowance": 100000,
                "other_allowances": 50000
            }
        }


class PeriodicSalaryIncomeDTO(BaseModel):
    """DTO for periodic salary income with multiple periods."""
    
    periods: List[PeriodicSalaryDataDTO] = Field(..., min_items=1, description="List of salary periods")
    
    class Config:
        schema_extra = {
            "example": {
                "periods": [
                    {
                        "period": {
                            "start_date": "2024-04-01",
                            "end_date": "2024-09-30",
                            "description": "Pre-increment period"
                        },
                        "basic_salary": 600000,
                        "hra_received": 240000,
                        "hra_city_type": "metro",
                        "actual_rent_paid": 300000
                    },
                    {
                        "period": {
                            "start_date": "2024-10-01",
                            "end_date": None,
                            "description": "Post-increment period"
                        },
                        "basic_salary": 800000,
                        "hra_received": 320000,
                        "hra_city_type": "metro",
                        "actual_rent_paid": 300000
                    }
                ]
            }
        }


class MidYearJoinerDTO(BaseModel):
    """DTO for mid-year joiner scenario."""
    
    joining_date: date = Field(..., description="Date of joining")
    salary_details: PeriodicSalaryDataDTO = Field(..., description="Salary details")
    
    class Config:
        schema_extra = {
            "example": {
                "joining_date": "2024-10-01",
                "salary_details": {
                    "period": {
                        "start_date": "2024-10-01",
                        "end_date": None,
                        "description": "Mid-year joining"
                    },
                    "basic_salary": 800000,
                    "hra_received": 320000,
                    "hra_city_type": "metro",
                    "actual_rent_paid": 300000
                }
            }
        }


class MidYearIncrementDTO(BaseModel):
    """DTO for mid-year increment scenario."""
    
    increment_date: date = Field(..., description="Date of increment")
    pre_increment_salary: PeriodicSalaryDataDTO = Field(..., description="Salary before increment")
    post_increment_salary: PeriodicSalaryDataDTO = Field(..., description="Salary after increment")
    
    class Config:
        schema_extra = {
            "example": {
                "increment_date": "2024-10-01",
                "pre_increment_salary": {
                    "period": {
                        "start_date": "2024-04-01",
                        "end_date": "2024-09-30",
                        "description": "Pre-increment period"
                    },
                    "basic_salary": 600000,
                    "hra_received": 240000,
                    "hra_city_type": "metro",
                    "actual_rent_paid": 300000
                },
                "post_increment_salary": {
                    "period": {
                        "start_date": "2024-10-01",
                        "end_date": None,
                        "description": "Post-increment period"
                    },
                    "basic_salary": 800000,
                    "hra_received": 320000,
                    "hra_city_type": "metro",
                    "actual_rent_paid": 300000
                }
            }
        }


# =============================================================================
# DEDUCTION DTOs
# =============================================================================

class DeductionSection80CDTO(BaseModel):
    """Section 80C deductions DTO."""
    life_insurance_premium: Decimal = Field(default=0, ge=0)
    epf_contribution: Decimal = Field(default=0, ge=0)
    ppf_contribution: Decimal = Field(default=0, ge=0)
    nsc_investment: Decimal = Field(default=0, ge=0)
    tax_saving_fd: Decimal = Field(default=0, ge=0)
    elss_investment: Decimal = Field(default=0, ge=0)
    home_loan_principal: Decimal = Field(default=0, ge=0)
    tuition_fees: Decimal = Field(default=0, ge=0)
    ulip_premium: Decimal = Field(default=0, ge=0)
    sukanya_samriddhi: Decimal = Field(default=0, ge=0)
    stamp_duty_property: Decimal = Field(default=0, ge=0)
    senior_citizen_savings: Decimal = Field(default=0, ge=0)
    other_80c_investments: Decimal = Field(default=0, ge=0)


class DeductionSection80DDTO(BaseModel):
    """Section 80D deductions DTO."""
    self_family_premium: Decimal = Field(default=0, ge=0)
    parent_premium: Decimal = Field(default=0, ge=0)
    preventive_health_checkup: Decimal = Field(default=0, ge=0)
    employee_age: int = Field(default=25, ge=18, le=100)
    parent_age: int = Field(default=55, ge=18, le=120)


class DeductionSection80GDTO(BaseModel):
    """Enhanced Section 80G deductions DTO with specific donation heads."""
    
    # 100% deduction without qualifying limit - Specific heads
    pm_relief_fund: Decimal = Field(default=0, ge=0)
    national_defence_fund: Decimal = Field(default=0, ge=0)
    national_foundation_communal_harmony: Decimal = Field(default=0, ge=0)
    zila_saksharta_samiti: Decimal = Field(default=0, ge=0)
    national_illness_assistance_fund: Decimal = Field(default=0, ge=0)
    national_blood_transfusion_council: Decimal = Field(default=0, ge=0)
    national_trust_autism_fund: Decimal = Field(default=0, ge=0)
    national_sports_fund: Decimal = Field(default=0, ge=0)
    national_cultural_fund: Decimal = Field(default=0, ge=0)
    technology_development_fund: Decimal = Field(default=0, ge=0)
    national_children_fund: Decimal = Field(default=0, ge=0)
    cm_relief_fund: Decimal = Field(default=0, ge=0)
    army_naval_air_force_funds: Decimal = Field(default=0, ge=0)
    swachh_bharat_kosh: Decimal = Field(default=0, ge=0)
    clean_ganga_fund: Decimal = Field(default=0, ge=0)
    drug_abuse_control_fund: Decimal = Field(default=0, ge=0)
    other_100_percent_wo_limit: Decimal = Field(default=0, ge=0)
    
    # 50% deduction without qualifying limit - Specific heads
    jn_memorial_fund: Decimal = Field(default=0, ge=0)
    pm_drought_relief: Decimal = Field(default=0, ge=0)
    indira_gandhi_memorial_trust: Decimal = Field(default=0, ge=0)
    rajiv_gandhi_foundation: Decimal = Field(default=0, ge=0)
    other_50_percent_wo_limit: Decimal = Field(default=0, ge=0)
    
    # 100% deduction with qualifying limit (10% of income) - Specific heads
    family_planning_donation: Decimal = Field(default=0, ge=0)
    indian_olympic_association: Decimal = Field(default=0, ge=0)
    other_100_percent_w_limit: Decimal = Field(default=0, ge=0)
    
    # 50% deduction with qualifying limit (10% of income) - Specific heads
    govt_charitable_donations: Decimal = Field(default=0, ge=0)
    housing_authorities_donations: Decimal = Field(default=0, ge=0)
    religious_renovation_donations: Decimal = Field(default=0, ge=0)
    other_charitable_donations: Decimal = Field(default=0, ge=0)
    other_50_percent_w_limit: Decimal = Field(default=0, ge=0)


class DeductionSection80EDTO(BaseModel):
    """Section 80E education loan interest DTO."""
    education_loan_interest: Decimal = Field(default=0, ge=0)
    relation: str = Field(default="Self", description="Self, Spouse, or Child")
    
    @validator('relation')
    def validate_relation(cls, v):
        if v not in ["Self", "Spouse", "Child"]:
            raise ValueError("Relation must be 'Self', 'Spouse', or 'Child'")
        return v


class DeductionSection80TTADTO(BaseModel):
    """Section 80TTA/80TTB interest income exemptions DTO."""
    savings_interest: Decimal = Field(default=0, ge=0)
    fd_interest: Decimal = Field(default=0, ge=0)
    rd_interest: Decimal = Field(default=0, ge=0)
    other_bank_interest: Decimal = Field(default=0, ge=0)
    age: int = Field(default=25, ge=18, le=100)


class OtherDeductionsDTO(BaseModel):
    """Other deductions DTO."""
    education_loan_interest: Decimal = Field(default=0, ge=0)
    charitable_donations: Decimal = Field(default=0, ge=0)
    savings_interest: Decimal = Field(default=0, ge=0)
    nps_contribution: Decimal = Field(default=0, ge=0)
    other_deductions: Decimal = Field(default=0, ge=0)


class TaxDeductionsDTO(BaseModel):
    """Complete comprehensive tax deductions DTO."""
    section_80c: Optional[DeductionSection80CDTO] = None
    section_80d: Optional[DeductionSection80DDTO] = None
    section_80g: Optional[DeductionSection80GDTO] = None
    section_80e: Optional[DeductionSection80EDTO] = None
    section_80tta_ttb: Optional[DeductionSection80TTADTO] = None
    other_deductions: Optional[OtherDeductionsDTO] = None


# =============================================================================
# ENHANCED CALCULATION REQUEST DTOs
# =============================================================================

class EnhancedTaxCalculationRequestDTO(BaseModel):
    """DTO for enhanced tax calculation request."""
    
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    regime_type: str = Field(..., description="Tax regime type ('old' or 'new')")
    age: int = Field(..., ge=18, le=100, description="Taxpayer age")
    
    # Salary income - can be simple or periodic
    salary_income: Optional[PeriodicSalaryIncomeDTO] = Field(None, description="Periodic salary income")
    simple_salary_income: Optional[SalaryIncomeDTO] = Field(None, description="Simple salary income")
    
    # Comprehensive deductions
    deductions: Optional[TaxDeductionsDTO] = Field(None, description="Comprehensive deductions")
    
    # Legacy simplified deduction fields for backward compatibility
    section_80c_investments: Decimal = Field(0, ge=0, description="Section 80C investments")
    section_80d_health_insurance: Decimal = Field(0, ge=0, description="Section 80D health insurance")
    section_80d_parents_health_insurance: Decimal = Field(0, ge=0, description="Section 80D parents health insurance")
    section_80e_education_loan: Decimal = Field(0, ge=0, description="Section 80E education loan interest")
    section_80g_donations: Decimal = Field(0, ge=0, description="Section 80G donations")
    section_80tta_savings_interest: Decimal = Field(0, ge=0, description="Section 80TTA savings interest")
    section_80ccd1b_nps: Decimal = Field(0, ge=0, description="Section 80CCD(1B) NPS")
    
    # Scenario-specific options
    calculate_surcharge_breakdown: bool = Field(True, description="Calculate detailed surcharge breakdown")
    include_projections: bool = Field(True, description="Include full-year projections")
    include_optimization_suggestions: bool = Field(True, description="Include optimization suggestions")
    
    @validator('regime_type')
    def validate_regime(cls, v):
        if v not in ["old", "new"]:
            raise ValueError("Regime must be 'old' or 'new'")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "tax_year": "2024-25",
                "regime_type": "old",
                "age": 30,
                "salary_income": {
                    "periods": [
                        {
                            "period": {
                                "start_date": "2024-04-01",
                                "end_date": "2024-09-30",
                                "description": "Pre-increment period"
                            },
                            "basic_salary": 600000,
                            "hra_received": 240000,
                            "hra_city_type": "metro",
                            "actual_rent_paid": 300000
                        }
                    ]
                },
                "section_80c_investments": 150000,
                "section_80d_health_insurance": 25000
            }
        }


class ScenarioComparisonRequestDTO(BaseModel):
    """DTO for comparing different scenarios."""
    
    base_request: EnhancedTaxCalculationRequestDTO = Field(..., description="Base calculation request")
    
    # Comparison scenarios
    compare_full_year_at_current: bool = Field(False, description="Compare with full year at current salary")
    compare_full_year_at_highest: bool = Field(False, description="Compare with full year at highest salary")
    compare_different_regime: bool = Field(False, description="Compare with different tax regime")
    
    class Config:
        schema_extra = {
            "example": {
                "base_request": {
                    "tax_year": "2024-25",
                    "regime_type": "old",
                    "age": 30,
                    "salary_income": {
                        "periods": [
                            {
                                "period": {
                                    "start_date": "2024-10-01",
                                    "end_date": None,
                                    "description": "Mid-year joining"
                                },
                                "basic_salary": 800000,
                                "hra_received": 320000,
                                "hra_city_type": "metro",
                                "actual_rent_paid": 300000
                            }
                        ]
                    },
                    "section_80c_investments": 150000
                },
                "compare_full_year_at_current": True,
                "compare_different_regime": True
            }
        }


# =============================================================================
# LEGACY REQUEST DTOs (for backward compatibility)
# =============================================================================

class CreateTaxationRecordRequest(BaseModel):
    """Request to create new taxation record with comprehensive income support."""
    user_id: str = Field(..., description="User ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2023-24')")
    
    # Core income (required for backward compatibility)
    salary_income: SalaryIncomeDTO
    deductions: Optional[TaxDeductionsDTO] = None
    
    # Comprehensive income components (optional)
    perquisites: Optional["PerquisitesDTO"] = None
    house_property_income: Optional["HousePropertyIncomeDTO"] = None
    multiple_house_properties: Optional["MultipleHousePropertiesDTO"] = None
    capital_gains_income: Optional["CapitalGainsIncomeDTO"] = None
    retirement_benefits: Optional["RetirementBenefitsDTO"] = None
    other_income: Optional["OtherIncomeDTO"] = None
    monthly_payroll: Optional["AnnualPayrollWithLWPDTO"] = None
    
    # Enhanced deductions (optional)
    comprehensive_deductions: Optional[TaxDeductionsDTO] = None
    
    regime: str = Field(default="old", description="Tax regime: 'old' or 'new'")
    age: int = Field(..., ge=18, le=100, description="Taxpayer age")
    
    @validator('regime')
    def validate_regime(cls, v):
        if v not in ["old", "new"]:
            raise ValueError("Regime must be 'old' or 'new'")
        return v


class UpdateSalaryIncomeRequest(BaseModel):
    """Request to update salary income."""
    taxation_id: str = Field(..., description="Taxation record ID")
    salary_income: SalaryIncomeDTO


class UpdateDeductionsRequest(BaseModel):
    """Request to update deductions."""
    taxation_id: str = Field(..., description="Taxation record ID")
    deductions: TaxDeductionsDTO


class ChangeRegimeRequest(BaseModel):
    """Request to change tax regime."""
    taxation_id: str = Field(..., description="Taxation record ID")
    new_regime: str = Field(..., description="New tax regime: 'old' or 'new'")
    
    @validator('new_regime')
    def validate_regime(cls, v):
        if v not in ["old", "new"]:
            raise ValueError("Regime must be 'old' or 'new'")
        return v


class CalculateTaxRequest(BaseModel):
    """Request to calculate tax."""
    taxation_id: str = Field(..., description="Taxation record ID")
    force_recalculate: bool = Field(default=False, description="Force recalculation even if current")


class CompareRegimesRequest(BaseModel):
    """Request to compare tax regimes."""
    taxation_id: str = Field(..., description="Taxation record ID")


class FinalizeRecordRequest(BaseModel):
    """Request to finalize tax record."""
    taxation_id: str = Field(..., description="Taxation record ID")


# =============================================================================
# CALCULATION RESPONSE DTOs
# =============================================================================

class SurchargeBreakdownDTO(BaseModel):
    """DTO for detailed surcharge breakdown."""
    
    applicable: bool = Field(..., description="Whether surcharge is applicable")
    rate: float = Field(..., description="Surcharge rate percentage")
    rate_description: str = Field(..., description="Description of surcharge rate")
    base_amount: float = Field(..., description="Base amount for surcharge calculation")
    surcharge_amount: float = Field(..., description="Calculated surcharge amount")
    income_slab: str = Field(..., description="Income slab for surcharge")
    marginal_relief_applicable: bool = Field(..., description="Whether marginal relief applies")
    marginal_relief_amount: float = Field(..., description="Marginal relief amount")
    effective_surcharge: float = Field(..., description="Effective surcharge after relief")


class TaxCalculationBreakdownDTO(BaseModel):
    """Tax calculation breakdown DTO."""
    regime_type: str
    taxpayer_age: int
    gross_income: Decimal
    total_exemptions: Decimal
    total_deductions: Decimal
    taxable_income: Decimal
    tax_before_rebate: Decimal
    rebate_87a: Decimal
    tax_after_rebate: Decimal
    surcharge: Decimal
    cess: Decimal
    total_tax_liability: Decimal
    effective_tax_rate: str
    monthly_tax_liability: Decimal


class PeriodicTaxCalculationResponseDTO(BaseModel):
    """DTO for enhanced tax calculation response."""
    
    # Basic tax calculation results
    gross_income: float = Field(..., description="Total gross income")
    total_exemptions: float = Field(..., description="Total exemptions")
    total_deductions: float = Field(..., description="Total deductions")
    taxable_income: float = Field(..., description="Taxable income")
    tax_before_rebate: float = Field(..., description="Tax before rebate")
    rebate_87a: float = Field(..., description="Rebate under Section 87A")
    tax_after_rebate: float = Field(..., description="Tax after rebate")
    surcharge: float = Field(..., description="Surcharge amount")
    cess: float = Field(..., description="Health and Education Cess")
    total_tax_liability: float = Field(..., description="Total tax liability")
    effective_tax_rate: float = Field(..., description="Effective tax rate percentage")
    
    # Enhanced details
    employment_periods: int = Field(..., description="Number of employment periods")
    total_employment_days: int = Field(..., description="Total employment days")
    is_mid_year_scenario: bool = Field(..., description="Whether it's a mid-year scenario")
    
    # Detailed breakdowns
    period_wise_income: List[Dict[str, Any]] = Field(..., description="Period-wise income breakdown")
    surcharge_breakdown: SurchargeBreakdownDTO = Field(..., description="Detailed surcharge breakdown")
    
    # Analysis and projections
    full_year_projection: Dict[str, Any] = Field(..., description="Full year projection")
    mid_year_impact: Dict[str, Any] = Field(..., description="Mid-year impact analysis")
    optimization_suggestions: List[str] = Field(..., description="Tax optimization suggestions")
    
    # Metadata
    regime_used: str = Field(..., description="Tax regime used")
    taxpayer_age: int = Field(..., description="Taxpayer age")
    calculation_breakdown: Dict[str, Any] = Field(..., description="Detailed calculation breakdown")


class ScenarioComparisonResponseDTO(BaseModel):
    """DTO for scenario comparison response."""
    
    base_calculation: PeriodicTaxCalculationResponseDTO = Field(..., description="Base calculation result")
    
    # Comparison results
    full_year_current_comparison: Optional[Dict[str, Any]] = Field(None, description="Full year at current salary comparison")
    full_year_highest_comparison: Optional[Dict[str, Any]] = Field(None, description="Full year at highest salary comparison")
    regime_comparison: Optional[Dict[str, Any]] = Field(None, description="Different regime comparison")
    
    # Summary
    recommendations: List[str] = Field(..., description="Recommendations based on comparison")
    best_scenario: Dict[str, Any] = Field(..., description="Best scenario analysis")


class TaxOptimizationSuggestionDTO(BaseModel):
    """DTO for tax optimization suggestions."""
    
    category: str = Field(..., description="Category of suggestion")
    suggestion: str = Field(..., description="Optimization suggestion")
    potential_savings: Optional[Decimal] = Field(None, description="Potential tax savings")
    investment_required: Optional[Decimal] = Field(None, description="Investment required")
    priority: str = Field(..., description="Priority level (High/Medium/Low)")
    
    class Config:
        schema_extra = {
            "example": {
                "category": "Section 80C",
                "suggestion": "Consider investing ₹50,000 more in ELSS to maximize Section 80C benefits",
                "potential_savings": 15000,
                "investment_required": 50000,
                "priority": "High"
            }
        }


# =============================================================================
# LEGACY RESPONSE DTOs
# =============================================================================

class TaxationRecordSummaryDTO(BaseModel):
    """Taxation record summary DTO."""
    taxation_id: str
    user_id: str
    organization_id: str
    tax_year: str
    regime: str
    age: int
    is_final: bool
    status: str
    gross_income: Optional[Decimal] = None
    taxable_income: Optional[Decimal] = None
    total_tax_liability: Optional[Decimal] = None
    monthly_tax: Optional[Decimal] = None
    effective_tax_rate: Optional[str] = None
    last_calculated: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class CreateTaxationRecordResponse(BaseModel):
    """Response for creating taxation record."""
    taxation_id: str
    user_id: str
    tax_year: str
    regime: str
    status: str
    message: str
    created_at: datetime


class CalculateTaxResponse(BaseModel):
    """Response for tax calculation."""
    taxation_id: str
    user_id: str
    tax_year: str
    regime: str
    calculation_breakdown: TaxCalculationBreakdownDTO
    calculated_at: datetime


class DetailedTaxBreakdownResponse(BaseModel):
    """Detailed tax breakdown response."""
    taxation_record: TaxationRecordSummaryDTO
    salary_breakdown: Dict[str, Any]
    deduction_breakdown: Dict[str, Any]
    tax_calculation: Dict[str, Any]
    validation_warnings: List[str]


class RegimeComparisonResponse(BaseModel):
    """Response for regime comparison."""
    taxation_id: str
    current_regime: str
    comparison_summary: Dict[str, Any]
    detailed_calculations: Dict[str, Any]
    recommendation: Dict[str, Any]
    savings_analysis: Dict[str, Any]
    key_differences: List[str]
    can_switch: bool


class TaxSavingSuggestionsResponse(BaseModel):
    """Tax saving suggestions response."""
    taxation_id: str
    current_regime: str
    total_current_deductions: Decimal
    suggestions: List[Dict[str, Any]]
    potential_annual_savings: Decimal


class TaxationRecordListResponse(BaseModel):
    """Response for listing taxation records."""
    records: List[TaxationRecordSummaryDTO]
    total_count: int
    page: int
    page_size: int


class UpdateResponse(BaseModel):
    """Generic update response."""
    taxation_id: str
    status: str
    message: str
    updated_at: datetime


class ErrorResponse(BaseModel):
    """Error response DTO."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# QUERY DTOs
# =============================================================================

class TaxationRecordQuery(BaseModel):
    """Query parameters for taxation records."""
    user_id: Optional[str] = None
    tax_year: Optional[str] = None
    regime: Optional[str] = None
    is_final: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    
    @validator('regime')
    def validate_regime(cls, v):
        if v is not None and v not in ["old", "new"]:
            raise ValueError("Regime must be 'old' or 'new'")
        return v


class TaxYearSummaryQuery(BaseModel):
    """Query for tax year summary."""
    user_id: str
    tax_year: str


class TaxAnalyticsQuery(BaseModel):
    """Query for tax analytics."""
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None
    regime: Optional[str] = None
    
    @validator('regime')
    def validate_regime(cls, v):
        if v is not None and v not in ["old", "new"]:
            raise ValueError("Regime must be 'old' or 'new'")
        return v


# =============================================================================
# ANALYTICS DTOs
# =============================================================================

class TaxAnalyticsResponse(BaseModel):
    """Tax analytics response."""
    period: str
    total_records: int
    average_tax_liability: Decimal
    regime_distribution: Dict[str, int]
    income_distribution: Dict[str, int]
    tax_savings_summary: Dict[str, Any]
    trends: List[Dict[str, Any]]


class TaxYearSummaryResponse(BaseModel):
    """Tax year summary response."""
    user_id: str
    tax_year: str
    total_records: int
    regimes_used: List[str]
    total_tax_liability: Decimal
    average_effective_rate: str
    total_tax_savings: Decimal
    records: List[TaxationRecordSummaryDTO]


# =============================================================================
# PERQUISITES DTOs
# =============================================================================

class AccommodationPerquisiteDTO(BaseModel):
    """Accommodation perquisite DTO."""
    accommodation_type: str = Field(..., description="Government, Employer-Owned, Employer-Leased, Hotel")
    city_population: str = Field(default="Below 15 lakhs", description="City population category")
    
    # For government accommodation
    license_fees: Decimal = Field(default=0, ge=0)
    employee_rent_payment: Decimal = Field(default=0, ge=0)
    
    # For employer-owned/leased
    basic_salary: Decimal = Field(default=0, ge=0)
    dearness_allowance: Decimal = Field(default=0, ge=0)
    
    # For employer-leased
    rent_paid_by_employer: Decimal = Field(default=0, ge=0)
    
    # For hotel accommodation
    hotel_charges: Decimal = Field(default=0, ge=0)
    stay_days: int = Field(default=0, ge=0)
    
    # Furniture related
    furniture_cost: Decimal = Field(default=0, ge=0)
    furniture_employee_payment: Decimal = Field(default=0, ge=0)
    is_furniture_owned_by_employer: bool = Field(default=True)
    
    @validator('accommodation_type')
    def validate_accommodation_type(cls, v):
        valid_types = ["Government", "Employer-Owned", "Employer-Leased", "Hotel"]
        if v not in valid_types:
            raise ValueError(f"Accommodation type must be one of: {valid_types}")
        return v
    
    @validator('city_population')
    def validate_city_population(cls, v):
        valid_populations = ["Above 40 lakhs", "Between 15-40 lakhs", "Below 15 lakhs"]
        if v not in valid_populations:
            raise ValueError(f"City population must be one of: {valid_populations}")
        return v


class CarPerquisiteDTO(BaseModel):
    """Car perquisite DTO."""
    car_use_type: str = Field(..., description="Personal, Business, Mixed")
    engine_capacity_cc: int = Field(default=1600, ge=0)
    months_used: int = Field(default=12, ge=1, le=12)
    
    # For personal use
    car_cost_to_employer: Decimal = Field(default=0, ge=0)
    other_vehicle_cost: Decimal = Field(default=0, ge=0)
    
    # For mixed use
    has_expense_reimbursement: bool = Field(default=False)
    driver_provided: bool = Field(default=False)
    
    @validator('car_use_type')
    def validate_car_use_type(cls, v):
        valid_types = ["Personal", "Business", "Mixed"]
        if v not in valid_types:
            raise ValueError(f"Car use type must be one of: {valid_types}")
        return v


class MedicalReimbursementDTO(BaseModel):
    """Medical reimbursement perquisite DTO."""
    medical_reimbursement_amount: Decimal = Field(default=0, ge=0)
    is_overseas_treatment: bool = Field(default=False)


class LTAPerquisiteDTO(BaseModel):
    """LTA perquisite DTO."""
    lta_amount_claimed: Decimal = Field(default=0, ge=0)
    lta_claimed_count: int = Field(default=0, ge=0)
    public_transport_cost: Decimal = Field(default=0, ge=0)


class InterestFreeConcessionalLoanDTO(BaseModel):
    """Interest-free/concessional loan perquisite DTO."""
    loan_amount: Decimal = Field(default=0, ge=0)
    outstanding_amount: Decimal = Field(default=0, ge=0)
    company_interest_rate: Decimal = Field(default=0, ge=0)
    sbi_interest_rate: Decimal = Field(default=8.5, ge=0)
    loan_months: int = Field(default=12, ge=1, le=12)


class ESOPPerquisiteDTO(BaseModel):
    """ESOP perquisite DTO."""
    shares_exercised: int = Field(default=0, ge=0)
    exercise_price: Decimal = Field(default=0, ge=0)
    allotment_price: Decimal = Field(default=0, ge=0)


class UtilitiesPerquisiteDTO(BaseModel):
    """Utilities perquisite DTO."""
    gas_paid_by_employer: Decimal = Field(default=0, ge=0)
    electricity_paid_by_employer: Decimal = Field(default=0, ge=0)
    water_paid_by_employer: Decimal = Field(default=0, ge=0)
    gas_paid_by_employee: Decimal = Field(default=0, ge=0)
    electricity_paid_by_employee: Decimal = Field(default=0, ge=0)
    water_paid_by_employee: Decimal = Field(default=0, ge=0)
    is_gas_manufactured_by_employer: bool = Field(default=False)
    is_electricity_manufactured_by_employer: bool = Field(default=False)
    is_water_manufactured_by_employer: bool = Field(default=False)


class FreeEducationPerquisiteDTO(BaseModel):
    """Free education perquisite DTO."""
    monthly_expenses_child1: Decimal = Field(default=0, ge=0)
    monthly_expenses_child2: Decimal = Field(default=0, ge=0)
    months_child1: int = Field(default=12, ge=0, le=12)
    months_child2: int = Field(default=12, ge=0, le=12)
    employer_maintained_1st_child: bool = Field(default=False)
    employer_maintained_2nd_child: bool = Field(default=False)


class MovableAssetUsageDTO(BaseModel):
    """Movable asset usage perquisite DTO."""
    asset_type: str = Field(..., description="Electronics, Motor Vehicle, Others")
    asset_value: Decimal = Field(default=0, ge=0)
    employee_payment: Decimal = Field(default=0, ge=0)
    is_employer_owned: bool = Field(default=True)
    
    @validator('asset_type')
    def validate_asset_type(cls, v):
        valid_types = ["Electronics", "Motor Vehicle", "Others"]
        if v not in valid_types:
            raise ValueError(f"Asset type must be one of: {valid_types}")
        return v


class MovableAssetTransferDTO(BaseModel):
    """Movable asset transfer perquisite DTO."""
    asset_type: str = Field(..., description="Electronics, Motor Vehicle, Others")
    asset_cost: Decimal = Field(default=0, ge=0)
    years_of_use: int = Field(default=0, ge=0)
    employee_payment: Decimal = Field(default=0, ge=0)
    
    @validator('asset_type')
    def validate_asset_type(cls, v):
        valid_types = ["Electronics", "Motor Vehicle", "Others"]
        if v not in valid_types:
            raise ValueError(f"Asset type must be one of: {valid_types}")
        return v


class LunchRefreshmentPerquisiteDTO(BaseModel):
    """Lunch refreshment perquisite DTO."""
    employer_cost: Decimal = Field(default=0, ge=0)
    employee_payment: Decimal = Field(default=0, ge=0)
    meal_days_per_year: int = Field(default=0, ge=0, le=365)


class GiftVoucherPerquisiteDTO(BaseModel):
    """Gift voucher perquisite DTO."""
    gift_voucher_amount: Decimal = Field(default=0, ge=0)


class MonetaryBenefitsPerquisiteDTO(BaseModel):
    """Monetary benefits perquisite DTO."""
    monetary_amount_paid_by_employer: Decimal = Field(default=0, ge=0)
    expenditure_for_official_purpose: Decimal = Field(default=0, ge=0)
    amount_paid_by_employee: Decimal = Field(default=0, ge=0)


class ClubExpensesPerquisiteDTO(BaseModel):
    """Club expenses perquisite DTO."""
    club_expenses_paid_by_employer: Decimal = Field(default=0, ge=0)
    club_expenses_paid_by_employee: Decimal = Field(default=0, ge=0)
    club_expenses_for_official_purpose: Decimal = Field(default=0, ge=0)


class DomesticHelpPerquisiteDTO(BaseModel):
    """Domestic help perquisite DTO."""
    domestic_help_paid_by_employer: Decimal = Field(default=0, ge=0)
    domestic_help_paid_by_employee: Decimal = Field(default=0, ge=0)


class PerquisitesDTO(BaseModel):
    """Complete perquisites DTO."""
    # Core perquisites
    accommodation: Optional[AccommodationPerquisiteDTO] = None
    car: Optional[CarPerquisiteDTO] = None
    
    # Medical and travel perquisites
    medical_reimbursement: Optional[MedicalReimbursementDTO] = None
    lta: Optional[LTAPerquisiteDTO] = None
    
    # Financial perquisites
    interest_free_loan: Optional[InterestFreeConcessionalLoanDTO] = None
    esop: Optional[ESOPPerquisiteDTO] = None
    
    # Utilities and facilities
    utilities: Optional[UtilitiesPerquisiteDTO] = None
    free_education: Optional[FreeEducationPerquisiteDTO] = None
    lunch_refreshment: Optional[LunchRefreshmentPerquisiteDTO] = None
    domestic_help: Optional[DomesticHelpPerquisiteDTO] = None
    
    # Asset-related perquisites
    movable_asset_usage: Optional[MovableAssetUsageDTO] = None
    movable_asset_transfer: Optional[MovableAssetTransferDTO] = None
    
    # Miscellaneous perquisites
    gift_voucher: Optional[GiftVoucherPerquisiteDTO] = None
    monetary_benefits: Optional[MonetaryBenefitsPerquisiteDTO] = None
    club_expenses: Optional[ClubExpensesPerquisiteDTO] = None


# =============================================================================
# HOUSE PROPERTY INCOME DTOs
# =============================================================================

class HousePropertyIncomeDTO(BaseModel):
    """House property income DTO."""
    property_type: str = Field(..., description="Self-Occupied, Let-Out, Deemed Let-Out")
    annual_rent_received: Decimal = Field(default=0, ge=0)
    municipal_taxes_paid: Decimal = Field(default=0, ge=0)
    home_loan_interest: Decimal = Field(default=0, ge=0)
    pre_construction_interest: Decimal = Field(default=0, ge=0)
    fair_rental_value: Decimal = Field(default=0, ge=0)
    standard_rent: Decimal = Field(default=0, ge=0)
    
    @validator('property_type')
    def validate_property_type(cls, v):
        valid_types = ["Self-Occupied", "Let-Out", "Deemed Let-Out"]
        if v not in valid_types:
            raise ValueError(f"Property type must be one of: {valid_types}")
        return v


class MultipleHousePropertiesDTO(BaseModel):
    """Multiple house properties DTO."""
    properties: List[HousePropertyIncomeDTO] = Field(..., min_items=1)


# =============================================================================
# CAPITAL GAINS DTOs
# =============================================================================

class CapitalGainsIncomeDTO(BaseModel):
    """Capital gains income DTO."""
    # Short Term Capital Gains
    stcg_111a_equity_stt: Decimal = Field(default=0, ge=0, description="STCG on equity with STT (15%)")
    stcg_other_assets: Decimal = Field(default=0, ge=0, description="STCG on other assets (slab rates)")
    
    # Long Term Capital Gains
    ltcg_112a_equity_stt: Decimal = Field(default=0, ge=0, description="LTCG on equity with STT (10%)")
    ltcg_other_assets: Decimal = Field(default=0, ge=0, description="LTCG on other assets (20%)")
    ltcg_debt_mf: Decimal = Field(default=0, ge=0, description="LTCG on debt mutual funds (20%)")


# =============================================================================
# RETIREMENT BENEFITS DTOs
# =============================================================================

class LeaveEncashmentDTO(BaseModel):
    """Leave encashment DTO."""
    leave_encashment_amount: Decimal = Field(default=0, ge=0)
    average_monthly_salary: Decimal = Field(default=0, ge=0)
    leave_days_encashed: int = Field(default=0, ge=0)
    is_govt_employee: bool = Field(default=False)
    during_employment: bool = Field(default=False)


class GratuityDTO(BaseModel):
    """Gratuity DTO."""
    gratuity_amount: Decimal = Field(default=0, ge=0)
    monthly_salary: Decimal = Field(default=0, ge=0)
    service_years: Decimal = Field(default=0, ge=0)
    is_govt_employee: bool = Field(default=False)


class VRSDTO(BaseModel):
    """VRS DTO."""
    vrs_amount: Decimal = Field(default=0, ge=0)
    monthly_salary: Decimal = Field(default=0, ge=0)
    age: int = Field(default=25, ge=18, le=100)
    service_years: Decimal = Field(default=0, ge=0)


class PensionDTO(BaseModel):
    """Pension DTO."""
    regular_pension: Decimal = Field(default=0, ge=0)
    commuted_pension: Decimal = Field(default=0, ge=0)
    total_pension: Decimal = Field(default=0, ge=0)
    is_govt_employee: bool = Field(default=False)
    gratuity_received: bool = Field(default=False)


class RetrenchmentCompensationDTO(BaseModel):
    """Retrenchment compensation DTO."""
    retrenchment_amount: Decimal = Field(default=0, ge=0)
    monthly_salary: Decimal = Field(default=0, ge=0)
    service_years: Decimal = Field(default=0, ge=0)


class RetirementBenefitsDTO(BaseModel):
    """Retirement benefits DTO."""
    leave_encashment: Optional[LeaveEncashmentDTO] = None
    gratuity: Optional[GratuityDTO] = None
    vrs: Optional[VRSDTO] = None
    pension: Optional[PensionDTO] = None
    retrenchment_compensation: Optional[RetrenchmentCompensationDTO] = None


# =============================================================================
# OTHER INCOME DTOs
# =============================================================================

class InterestIncomeDTO(BaseModel):
    """Interest income DTO."""
    savings_account_interest: Decimal = Field(default=0, ge=0)
    fixed_deposit_interest: Decimal = Field(default=0, ge=0)
    recurring_deposit_interest: Decimal = Field(default=0, ge=0)
    other_bank_interest: Decimal = Field(default=0, ge=0)
    age: int = Field(default=25, ge=18, le=100)


class OtherIncomeDTO(BaseModel):
    """Other income DTO."""
    interest_income: Optional[InterestIncomeDTO] = None
    dividend_income: Decimal = Field(default=0, ge=0)
    gifts_received: Decimal = Field(default=0, ge=0)
    business_professional_income: Decimal = Field(default=0, ge=0)
    other_miscellaneous_income: Decimal = Field(default=0, ge=0)


# =============================================================================
# MONTHLY PAYROLL DTOs
# =============================================================================

class LWPDetailsDTO(BaseModel):
    """LWP details DTO."""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    lwp_days: int = Field(..., ge=0, le=31)
    working_days_in_month: int = Field(..., ge=1, le=31)


class MonthlyPayrollDTO(BaseModel):
    """Monthly payroll DTO."""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    base_monthly_gross: Decimal = Field(..., ge=0)
    lwp_days: int = Field(default=0, ge=0, le=31)
    working_days_in_month: int = Field(default=30, ge=1, le=31)


class AnnualPayrollWithLWPDTO(BaseModel):
    """Annual payroll with LWP DTO."""
    monthly_payrolls: List[MonthlyPayrollDTO] = Field(..., min_items=1, max_items=12)
    annual_salary: Decimal = Field(..., ge=0)
    total_lwp_days: int = Field(default=0, ge=0)
    lwp_details: List[LWPDetailsDTO] = Field(default=[])


# =============================================================================
# COMPREHENSIVE TAX INPUT DTO
# =============================================================================

class ComprehensiveTaxInputDTO(BaseModel):
    """Complete tax input DTO including all income sources."""
    
    # Basic details
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    regime_type: str = Field(..., description="Tax regime type ('old' or 'new')")
    age: int = Field(..., ge=18, le=100, description="Taxpayer age")
    
    # Income sources
    salary_income: Optional[SalaryIncomeDTO] = None
    periodic_salary_income: Optional[PeriodicSalaryIncomeDTO] = None
    perquisites: Optional[PerquisitesDTO] = None
    house_property_income: Optional[HousePropertyIncomeDTO] = None
    multiple_house_properties: Optional[MultipleHousePropertiesDTO] = None
    capital_gains_income: Optional[CapitalGainsIncomeDTO] = None
    retirement_benefits: Optional[RetirementBenefitsDTO] = None
    other_income: Optional[OtherIncomeDTO] = None
    monthly_payroll: Optional[AnnualPayrollWithLWPDTO] = None
    
    # Deductions
    deductions: Optional[TaxDeductionsDTO] = None
    
    @validator('regime_type')
    def validate_regime(cls, v):
        if v.lower() not in ["old", "new"]:
            raise ValueError("Regime type must be 'old' or 'new'")
        return v.lower()


class ComprehensiveTaxOutputDTO(BaseModel):
    """Complete tax output DTO including all income sources."""
    
    # Basic details
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    regime_type: str = Field(..., description="Tax regime type ('old' or 'new')")
    age: int = Field(..., ge=18, le=100, description="Taxpayer age")
    is_govt_employee: bool = False
    employee_id: str = Field(..., description="Employee ID")
    
    # Income sources
    salary_income: Optional[SalaryIncomeDTO] = None
    periodic_salary_income: Optional[PeriodicSalaryIncomeDTO] = None
    perquisites: Optional[PerquisitesDTO] = None
    house_property_income: Optional[HousePropertyIncomeDTO] = None
    multiple_house_properties: Optional[MultipleHousePropertiesDTO] = None
    capital_gains_income: Optional[CapitalGainsIncomeDTO] = None
    retirement_benefits: Optional[RetirementBenefitsDTO] = None
    other_income: Optional[OtherIncomeDTO] = None
    monthly_payroll: Optional[AnnualPayrollWithLWPDTO] = None
    
    # Deductions
    deductions: Optional[TaxDeductionsDTO] = None

# =============================================================================
# EMPLOYEE SELECTION DTOs
# =============================================================================

class EmployeeSelectionDTO(BaseModel):
    """
    DTO for employee selection in taxation module.
    Provides basic employee information needed for tax management.
    """
    employee_id: str
    user_name: str
    email: str
    department: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    joining_date: Optional[str] = None
    current_salary: Optional[float] = None
    
    # Tax-related information if available
    has_tax_record: bool = False
    tax_year: Optional[str] = None
    filing_status: Optional[str] = None
    total_tax: Optional[float] = None
    regime: Optional[str] = None
    last_updated: Optional[str] = None


class EmployeeSelectionQuery(BaseModel):
    """Query parameters for employee selection"""
    skip: int = 0
    limit: int = 20
    search: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    has_tax_record: Optional[bool] = None
    tax_year: Optional[str] = None


class EmployeeSelectionResponse(BaseModel):
    """Response for employee selection endpoint"""
    total: int
    employees: List[EmployeeSelectionDTO]
    skip: int
    limit: int
    has_more: bool 