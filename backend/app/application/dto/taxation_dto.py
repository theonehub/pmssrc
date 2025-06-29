"""
Comprehensive Taxation DTOs
Data Transfer Objects for taxation API covering all scenarios including mid-year and periodic calculations
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator, model_validator


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
    """Basic salary income DTO with comprehensive allowance fields."""
    # Core salary components
    basic_salary: Decimal = Field(..., ge=0)
    dearness_allowance: Decimal = Field(default=0, ge=0)
    hra_provided: Decimal = Field(default=0, ge=0)
    bonus: Decimal = Field(default=0, ge=0)
    commission: Decimal = Field(default=0, ge=0)
    special_allowance: Decimal = Field(default=0, ge=0)

    # Effective date fields for salary revisions
    effective_from: Optional[date] = Field(None, description="Effective from date for salary revision")
    effective_till: Optional[date] = Field(None, description="Effective till date for salary revision")
    
    # Additional detailed allowances from frontend
    city_compensatory_allowance: Decimal = Field(default=0, ge=0)
    rural_allowance: Decimal = Field(default=0, ge=0)
    proctorship_allowance: Decimal = Field(default=0, ge=0)
    wardenship_allowance: Decimal = Field(default=0, ge=0)
    project_allowance: Decimal = Field(default=0, ge=0)
    deputation_allowance: Decimal = Field(default=0, ge=0)
    interim_relief: Decimal = Field(default=0, ge=0)
    tiffin_allowance: Decimal = Field(default=0, ge=0)
    overtime_allowance: Decimal = Field(default=0, ge=0)
    servant_allowance: Decimal = Field(default=0, ge=0)
    hills_high_altd_allowance: Decimal = Field(default=0, ge=0)
    hills_high_altd_exemption_limit: Decimal = Field(default=0, ge=0)
    border_remote_allowance: Decimal = Field(default=0, ge=0)
    border_remote_exemption_limit: Decimal = Field(default=0, ge=0)
    transport_employee_allowance: Decimal = Field(default=0, ge=0)
    children_education_allowance: Decimal = Field(default=0, ge=0)
    children_education_count: int = Field(default=0, ge=0)
    children_education_months: int = Field(default=0, ge=0, le=12)
    hostel_allowance: Decimal = Field(default=0, ge=0)
    hostel_count: int = Field(default=0, ge=0)
    hostel_months: int = Field(default=0, ge=0, le=12)
    transport_months: int = Field(default=0, ge=0, le=12)
    underground_mines_allowance: Decimal = Field(default=0, ge=0)
    underground_mines_months: int = Field(default=0, ge=0, le=12)
    govt_employee_entertainment_allowance: Decimal = Field(default=0, ge=0)
    govt_employees_outside_india_allowance: Decimal = Field(default=0, ge=0)
    supreme_high_court_judges_allowance: Decimal = Field(default=0, ge=0)
    judge_compensatory_allowance: Decimal = Field(default=0, ge=0)
    section_10_14_special_allowances: Decimal = Field(default=0, ge=0)
    travel_on_tour_allowance: Decimal = Field(default=0, ge=0)
    tour_daily_charge_allowance: Decimal = Field(default=0, ge=0)
    conveyance_in_performace_of_duties: Decimal = Field(default=0, ge=0)
    helper_in_performace_of_duties: Decimal = Field(default=0, ge=0)
    academic_research: Decimal = Field(default=0, ge=0)
    uniform_allowance: Decimal = Field(default=0, ge=0)
    any_other_allowance_exemption: Decimal = Field(default=0, ge=0)
    
    @validator('effective_till')
    def validate_effective_till(cls, v, values):
        if v and 'effective_from' in values and values['effective_from'] and v <= values['effective_from']:
            raise ValueError("effective_till must be after effective_from")
        return v


class PeriodicSalaryDataDTO(BaseModel):
    """DTO for salary data in a specific period with comprehensive allowance fields."""
    
    period: EmploymentPeriodDTO
    # Core salary components
    basic_salary: Decimal = Field(..., gt=0, description="Basic salary amount")
    dearness_allowance: Decimal = Field(0, ge=0, description="Dearness allowance")
    hra_provided: Decimal = Field(0, ge=0, description="HRA provided")
    hra_city_type: str = Field("non_metro", description="City type for HRA calculation")
    actual_rent_paid: Decimal = Field(0, ge=0, description="Actual rent paid")
    special_allowance: Decimal = Field(0, ge=0, description="Special allowance")
    bonus: Decimal = Field(0, ge=0, description="Bonus")
    commission: Decimal = Field(0, ge=0, description="Commission")
    
    # Additional detailed allowances from frontend
    city_compensatory_allowance: Decimal = Field(default=0, ge=0)
    rural_allowance: Decimal = Field(default=0, ge=0)
    proctorship_allowance: Decimal = Field(default=0, ge=0)
    wardenship_allowance: Decimal = Field(default=0, ge=0)
    project_allowance: Decimal = Field(default=0, ge=0)
    deputation_allowance: Decimal = Field(default=0, ge=0)
    interim_relief: Decimal = Field(default=0, ge=0)
    tiffin_allowance: Decimal = Field(default=0, ge=0)
    overtime_allowance: Decimal = Field(default=0, ge=0)
    servant_allowance: Decimal = Field(default=0, ge=0)

    hills_high_altd_allowance: Decimal = Field(default=0, ge=0)
    hills_high_altd_exemption_limit: Decimal = Field(default=0, ge=0)
    border_remote_allowance: Decimal = Field(default=0, ge=0)
    border_remote_exemption_limit: Decimal = Field(default=0, ge=0)
    transport_employee_allowance: Decimal = Field(default=0, ge=0)
    children_education_allowance: Decimal = Field(default=0, ge=0)
    children_education_count: int = Field(default=0, ge=0)
    children_education_months: int = Field(default=0, ge=0, le=12)
    hostel_allowance: Decimal = Field(default=0, ge=0)
    hostel_count: int = Field(default=0, ge=0)
    hostel_months: int = Field(default=0, ge=0, le=12)

    transport_months: int = Field(default=0, ge=0, le=12)
    underground_mines_allowance: Decimal = Field(default=0, ge=0)
    underground_mines_months: int = Field(default=0, ge=0, le=12)
    
    govt_employee_entertainment_allowance: Decimal = Field(default=0, ge=0)
    govt_employees_outside_india_allowance: Decimal = Field(default=0, ge=0)
    supreme_high_court_judges_allowance: Decimal = Field(default=0, ge=0)
    judge_compensatory_allowance: Decimal = Field(default=0, ge=0)
    section_10_14_special_allowances: Decimal = Field(default=0, ge=0)
    travel_on_tour_allowance: Decimal = Field(default=0, ge=0)
    tour_daily_charge_allowance: Decimal = Field(default=0, ge=0)
    conveyance_in_performace_of_duties: Decimal = Field(default=0, ge=0)
    helper_in_performace_of_duties: Decimal = Field(default=0, ge=0)
    academic_research: Decimal = Field(default=0, ge=0)
    uniform_allowance: Decimal = Field(default=0, ge=0)
    any_other_allowance_exemption: Decimal = Field(default=0, ge=0)
    
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
                "hra_provided": 240000,
                "hra_city_type": "metro",
                "bonus": 100000,
                "commission": 50000,
                "actual_rent_paid": 300000,
                "special_allowance": 100000,
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
                        "hra_provided": 240000,
                        "hra_city_type": "metro",
                        "actual_rent_paid": 300000,
                        "bonus": 100000,
                        "commission": 50000
                    },
                    {
                        "period": {
                            "start_date": "2024-10-01",
                            "end_date": None,
                            "description": "Post-increment period"
                        },
                        "basic_salary": 800000,
                        "hra_provided": 320000,
                        "hra_city_type": "metro",
                        "actual_rent_paid": 300000,
                        "bonus": 100000,
                        "commission": 50000
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
                    "hra_provided": 320000,
                    "hra_city_type": "metro",
                    "actual_rent_paid": 300000,
                    "bonus": 100000,
                    "commission": 50000
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
                    "hra_provided": 240000,
                    "hra_city_type": "metro",
                    "actual_rent_paid": 300000,
                    "bonus": 100000,
                    "commission": 50000
                },
                "post_increment_salary": {
                    "period": {
                        "start_date": "2024-10-01",
                        "end_date": None,
                        "description": "Post-increment period"
                    },
                    "basic_salary": 800000,
                    "hra_provided": 320000,
                    "hra_city_type": "metro",
                    "actual_rent_paid": 300000,
                    "bonus": 100000,
                    "commission": 50000
                }
            }
        }


# =============================================================================
# DEDUCTION DTOs
# =============================================================================

class TaxDeductionsDTO(BaseModel):
    """Complete comprehensive tax deductions DTO with flat structure for frontend compatibility."""
    
    # HRA Exemption fields
    actual_rent_paid: Decimal = Field(default=0, ge=0, description="Actual rent paid for HRA exemption")
    hra_city_type: str = Field(default="non_metro", description="City type for HRA: metro or non_metro")
    
    # Section 80C fields
    life_insurance_premium: Decimal = Field(default=0, ge=0, description="Life insurance premium")
    epf_contribution: Decimal = Field(default=0, ge=0, description="EPF contribution")
    ppf_contribution: Decimal = Field(default=0, ge=0, description="PPF contribution")
    nsc_investment: Decimal = Field(default=0, ge=0, description="NSC investment")
    tax_saving_fd: Decimal = Field(default=0, ge=0, description="Tax saving fixed deposits")
    elss_investment: Decimal = Field(default=0, ge=0, description="ELSS investment")
    home_loan_principal: Decimal = Field(default=0, ge=0, description="Home loan principal repayment")
    tuition_fees: Decimal = Field(default=0, ge=0, description="Tuition fees")
    ulip_premium: Decimal = Field(default=0, ge=0, description="ULIP premium")
    sukanya_samriddhi: Decimal = Field(default=0, ge=0, description="Sukanya Samriddhi")
    stamp_duty_property: Decimal = Field(default=0, ge=0, description="Stamp duty on property")
    senior_citizen_savings: Decimal = Field(default=0, ge=0, description="Senior citizen savings")
    other_80c_investments: Decimal = Field(default=0, ge=0, description="Other 80C investments")
    
    # Section 80CCC fields
    pension_plan_insurance_company: Decimal = Field(default=0, ge=0, description="Pension plan from insurance company")
    
    # Section 80CCD fields
    nps_contribution_10_percent: Decimal = Field(default=0, ge=0, description="NPS contribution (10% of salary)")
    additional_nps_50k: Decimal = Field(default=0, ge=0, description="Additional NPS contribution (₹50K limit)")
    employer_nps_contribution: Decimal = Field(default=0, ge=0, description="Employer NPS contribution")
    
    # Section 80D fields
    self_family_premium: Decimal = Field(default=0, ge=0, description="Health insurance premium for self and family")
    parent_premium: Decimal = Field(default=0, ge=0, description="Health insurance premium for parents")
    preventive_health_checkup: Decimal = Field(default=0, ge=0, description="Preventive health checkup")
    employee_age: int = Field(default=25, ge=18, le=100, description="Employee age for 80D calculation")
    parent_age: int = Field(default=55, ge=18, le=120, description="Parent age for 80D calculation")
    
    # Section 80DD fields (Disability - Dependent)
    disability_amount: Decimal = Field(default=0, ge=0, description="Disability deduction amount")
    disability_relation: str = Field(default="Parents", description="Relation for disability deduction")
    disability_percentage: str = Field(default="40-79%", description="Disability percentage")
    
    # Section 80DDB fields (Medical Treatment)
    medical_expenses: Decimal = Field(default=0, ge=0, description="Medical expenses for specified diseases")
    medical_relation: str = Field(default="Self", description="Relation for medical expenses")
    dependent_age: int = Field(default=25, ge=18, le=120, description="Dependent age for medical expenses")
    
    # Section 80E fields
    education_loan_interest: Decimal = Field(default=0, ge=0, description="Education loan interest")
    education_loan_relation: str = Field(default="Self", description="Relation for education loan")
    
    # Section 80EEB fields
    ev_loan_interest: Decimal = Field(default=0, ge=0, description="Electric vehicle loan interest")
    ev_purchase_date: Optional[str] = Field(None, description="EV purchase date")
    
    # Section 80G fields (Charitable Donations)
    donation_100_percent_without_limit: Decimal = Field(default=0, ge=0, description="100% donation without limit")
    donation_50_percent_without_limit: Decimal = Field(default=0, ge=0, description="50% donation without limit")
    donation_100_percent_with_limit: Decimal = Field(default=0, ge=0, description="100% donation with limit")
    donation_50_percent_with_limit: Decimal = Field(default=0, ge=0, description="50% donation with limit")
    
    # Section 80GGC fields
    political_party_contribution: Decimal = Field(default=0, ge=0, description="Political party contribution")
    
    # Section 80U fields (Self Disability)
    self_disability_amount: Decimal = Field(default=0, ge=0, description="Self disability deduction amount")
    self_disability_percentage: str = Field(default="40-79%", description="Self disability percentage")
    
    # Section 80TTA/TTB fields
    savings_account_interest: Decimal = Field(default=0, ge=0, description="Savings account interest")
    deposit_interest_senior: Decimal = Field(default=0, ge=0, description="Deposit interest for senior citizens")
    interest_age: int = Field(default=25, ge=18, le=100, description="Age for interest exemption")
    
    # Legacy fields for backward compatibility
    section_80c_investments: Decimal = Field(default=0, ge=0, description="Total Section 80C investments (legacy)")
    section_80d_health_insurance: Decimal = Field(default=0, ge=0, description="Section 80D health insurance (legacy)")
    section_80d_parents_health_insurance: Decimal = Field(default=0, ge=0, description="Section 80D parents health insurance (legacy)")
    section_80e_education_loan: Decimal = Field(default=0, ge=0, description="Section 80E education loan (legacy)")
    section_80g_donations: Decimal = Field(default=0, ge=0, description="Section 80G donations (legacy)")
    section_80tta_savings_interest: Decimal = Field(default=0, ge=0, description="Section 80TTA savings interest (legacy)")
    section_80ccd1b_nps: Decimal = Field(default=0, ge=0, description="Section 80CCD(1B) NPS (legacy)")
    
    @validator('hra_city_type')
    def validate_hra_city_type(cls, v):
        if v not in ["metro", "non_metro"]:
            raise ValueError("HRA city type must be 'metro' or 'non_metro'")
        return v
    
    @validator('disability_relation')
    def validate_disability_relation(cls, v):
        valid_relations = ["Self", "Spouse", "Child", "Parents", "Sibling"]
        if v not in valid_relations:
            raise ValueError(f"Disability relation must be one of: {valid_relations}")
        return v
    
    @validator('disability_percentage')
    def validate_disability_percentage(cls, v):
        valid_percentages = ["40-79%", "80%+", "More than 80%"]
        if v not in valid_percentages:
            raise ValueError(f"Disability percentage must be one of: {valid_percentages}")
        return v
    
    @validator('medical_relation')
    def validate_medical_relation(cls, v):
        valid_relations = ["Self", "Spouse", "Child", "Parents", "Sibling"]
        if v not in valid_relations:
            raise ValueError(f"Medical relation must be one of: {valid_relations}")
        return v
    
    @validator('education_loan_relation')
    def validate_education_loan_relation(cls, v):
        valid_relations = ["Self", "Spouse", "Child"]
        if v not in valid_relations:
            raise ValueError(f"Education loan relation must be one of: {valid_relations}")
        return v
    
    @validator('self_disability_percentage')
    def validate_self_disability_percentage(cls, v):
        valid_percentages = ["40-79%", "80%+", "More than 80%"]
        if v not in valid_percentages:
            raise ValueError(f"Self disability percentage must be one of: {valid_percentages}")
        return v
    
    def to_nested_structure(self) -> Dict[str, Any]:
        """Convert flat structure to nested structure for entity conversion."""
        return {
            "section_80c": {
                "life_insurance_premium": self.life_insurance_premium,
                "epf_contribution": self.epf_contribution,
                "ppf_contribution": self.ppf_contribution,
                "nsc_investment": self.nsc_investment,
                "tax_saving_fd": self.tax_saving_fd,
                "elss_investment": self.elss_investment,
                "home_loan_principal": self.home_loan_principal,
                "tuition_fees": self.tuition_fees,
                "ulip_premium": self.ulip_premium,
                "sukanya_samriddhi": self.sukanya_samriddhi,
                "stamp_duty_property": self.stamp_duty_property,
                "senior_citizen_savings": self.senior_citizen_savings,
                "other_80c_investments": self.other_80c_investments,
            },
            "section_80ccc": {
                "pension_fund_contribution": self.pension_plan_insurance_company,
            },
            "section_80ccd": {
                "employee_nps_contribution": self.nps_contribution_10_percent,
                "additional_nps_contribution": self.additional_nps_50k,
                "employer_nps_contribution": self.employer_nps_contribution,
            },
            "section_80d": {
                "self_family_premium": self.self_family_premium,
                "parent_premium": self.parent_premium,
                "preventive_health_checkup": self.preventive_health_checkup,
                "employee_age": self.employee_age,
                "parent_age": self.parent_age,
            },
            "section_80dd": {
                "relation": self.disability_relation,
                "disability_percentage": self.disability_percentage,
            },
            "section_80ddb": {
                "dependent_age": self.dependent_age,
                "medical_expenses": self.medical_expenses,
                "relation": self.medical_relation,
            },
            "section_80e": {
                "education_loan_interest": self.education_loan_interest,
                "relation": self.education_loan_relation,
            },
            "section_80eeb": {
                "ev_loan_interest": self.ev_loan_interest,
                "ev_purchase_date": self.ev_purchase_date,
            },
            "section_80g": {
                "other_100_percent_wo_limit": self.donation_100_percent_without_limit,
                "other_50_percent_wo_limit": self.donation_50_percent_without_limit,
                "other_100_percent_w_limit": self.donation_100_percent_with_limit,
                "other_50_percent_w_limit": self.donation_50_percent_with_limit,
            },
            "section_80ggc": {
                "political_party_contribution": self.political_party_contribution,
            },
            "section_80u": {
                "disability_percentage": self.self_disability_percentage,
            },
            "section_80tta_ttb": {
                "savings_interest": self.savings_account_interest,
                "fd_interest": self.deposit_interest_senior,
                "rd_interest": Decimal(0),
                "post_office_interest": Decimal(0),
                "age": self.interest_age,
            },
            "hra_exemption": {
                "actual_rent_paid": self.actual_rent_paid,
                "hra_city_type": self.hra_city_type,
            },
        }


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
                            "hra_provided": 240000,
                            "hra_city_type": "metro",
                            "actual_rent_paid": 300000,
                            "bonus": 100000,
                            "commission": 50000
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
                                "hra_provided": 320000,
                                "hra_city_type": "metro",
                                "actual_rent_paid": 300000,
                                "bonus": 100000,
                                "commission": 50000
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
    employee_id: Optional[str] = Field(None, description="User ID (deprecated, use employee_id)")
    employee_id: Optional[str] = Field(None, description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2023-24')")
    
    # Core income (required for backward compatibility)
    salary_income: Optional[SalaryIncomeDTO] = None
    deductions: Optional[TaxDeductionsDTO] = None
    
    # Comprehensive income components (optional)
    perquisites: Optional["PerquisitesDTO"] = None
    house_property_income: Optional["HousePropertyIncomeDTO"] = None
    multiple_house_properties: Optional["MultipleHousePropertiesDTO"] = None
    capital_gains_income: Optional["CapitalGainsIncomeDTO"] = None
    retirement_benefits: Optional["RetirementBenefitsDTO"] = None
    other_income: Optional["OtherIncomeDTO"] = None
    monthly_payroll: Optional["PayoutMonthlyProjectionDTO"] = None
    
    # Enhanced deductions (optional)
    comprehensive_deductions: Optional[TaxDeductionsDTO] = None
    
    regime: str = Field(default="old", description="Tax regime: 'old' or 'new'")
    age: int = Field(..., ge=18, le=100, description="Taxpayer age")
    
    @validator('regime')
    def validate_regime(cls, v):
        if v not in ["old", "new"]:
            raise ValueError("Regime must be 'old' or 'new'")
        return v
    
    @model_validator(mode='before')
    @classmethod
    def validate_employee_identification(cls, values):
        """Ensure either employee_id or employee_id is provided and map employee_id to employee_id."""
        employee_id = values.get('employee_id')
        employee_id = values.get('employee_id')
        
        if not employee_id and not employee_id:
            raise ValueError("Either employee_id or employee_id must be provided")
        
        # If employee_id is provided but employee_id is not, map employee_id to employee_id
        if employee_id and not employee_id:
            values['employee_id'] = employee_id
        
        # If both are provided, ensure they match
        if employee_id and employee_id and employee_id != employee_id:
            raise ValueError("employee_id and employee_id must match if both are provided")
        
        return values


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
    employee_id: str
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
    employee_id: str
    tax_year: str
    regime: str
    status: str
    message: str
    created_at: datetime


class CalculateTaxResponse(BaseModel):
    """Response for tax calculation."""
    taxation_id: str
    employee_id: str
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
    employee_id: Optional[str] = None
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
    employee_id: str
    tax_year: str


class TaxAnalyticsQuery(BaseModel):
    """Query for tax analytics."""
    employee_id: Optional[str] = None
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
    employee_id: str
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

class PerquisitesDTO(BaseModel):
    """Complete perquisites DTO with flat structure for frontend compatibility."""
    
    # Accommodation perquisite fields
    accommodation_type: str = Field(default="Employer-Owned", description="Government, Employer-Owned, Employer-Leased, Hotel")
    city_population: str = Field(default="Below 15 lakhs", description="City population category")
    license_fees: Decimal = Field(default=0, ge=0, description="License fees for government accommodation")
    employee_rent_payment: Decimal = Field(default=0, ge=0, description="Employee rent payment")
    rent_paid_by_employer: Decimal = Field(default=0, ge=0, description="Rent paid by employer")
    hotel_charges: Decimal = Field(default=0, ge=0, description="Hotel charges")
    stay_days: int = Field(default=0, ge=0, description="Stay days in hotel")
    furniture_cost: Decimal = Field(default=0, ge=0, description="Furniture cost")
    furniture_employee_payment: Decimal = Field(default=0, ge=0, description="Furniture employee payment")
    is_furniture_owned_by_employer: bool = Field(default=False, description="Is furniture owned by employer")
    
    # Car perquisite fields
    car_use_type: str = Field(default="Personal", description="Personal, Business, Mixed")
    engine_capacity_cc: int = Field(default=1600, ge=0, description="Engine capacity in CC")
    months_used: int = Field(default=12, ge=0, le=12, description="Months used")
    car_cost_to_employer: Decimal = Field(default=0, ge=0, description="Car cost to employer")
    other_vehicle_cost: Decimal = Field(default=0, ge=0, description="Other vehicle cost")
    has_expense_reimbursement: bool = Field(default=False, description="Has expense reimbursement")
    driver_provided: bool = Field(default=False, description="Driver provided")
    
    # Medical reimbursement fields
    medical_reimbursement_amount: Decimal = Field(default=0, ge=0, description="Medical reimbursement amount")
    is_overseas_treatment: bool = Field(default=False, description="Is overseas treatment")
    
    # LTA fields
    lta_amount_claimed: Decimal = Field(default=0, ge=0, description="LTA amount claimed")
    lta_claimed_count: int = Field(default=0, ge=0, description="LTA claimed count")
    public_transport_cost: Decimal = Field(default=0, ge=0, description="Public transport cost")
    
    # ESOP fields
    esop_exercise_value: Decimal = Field(default=0, ge=0, description="ESOP exercise value")
    esop_fair_market_value: Decimal = Field(default=0, ge=0, description="ESOP fair market value")
    esop_shares_exercised: int = Field(default=0, ge=0, description="ESOP shares exercised")
    
    # Free education fields
    free_education_amount: Decimal = Field(default=0, ge=0, description="Free education amount")
    is_children_education: bool = Field(default=True, description="Is children education")
    
    # Utilities fields
    gas_electricity_water_amount: Decimal = Field(default=0, ge=0, description="Gas, electricity, water amount")
    
    # Interest free loan fields
    loan_amount: Decimal = Field(default=0, ge=0, description="Loan amount")
    interest_rate_charged: Decimal = Field(default=0, ge=0, description="Interest rate charged")
    sbi_rate: Decimal = Field(default=6.5, ge=0, description="SBI rate")
    
    # Movable assets fields
    movable_asset_value: Decimal = Field(default=0, ge=0, description="Movable asset value")
    asset_usage_months: int = Field(default=12, ge=0, le=12, description="Asset usage months")
    
    # Other perquisites fields
    lunch_refreshment_amount: Decimal = Field(default=0, ge=0, description="Lunch refreshment amount")
    domestic_help_amount: Decimal = Field(default=0, ge=0, description="Domestic help amount")
    other_perquisites_amount: Decimal = Field(default=0, ge=0, description="Other perquisites amount")
    
    # Additional fields for backward compatibility
    basic_salary: Decimal = Field(default=0, ge=0, description="Basic salary for accommodation calculation")
    dearness_allowance: Decimal = Field(default=0, ge=0, description="Dearness allowance for accommodation calculation")
    
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
    
    @validator('car_use_type')
    def validate_car_use_type(cls, v):
        valid_types = ["Personal", "Business", "Mixed"]
        if v not in valid_types:
            raise ValueError(f"Car use type must be one of: {valid_types}")
        return v
    
    def to_nested_structure(self) -> Dict[str, Any]:
        """Convert flat structure to nested structure for backward compatibility."""
        return {
            "accommodation": {
                "accommodation_type": self.accommodation_type,
                "city_population": self.city_population,
                "license_fees": self.license_fees,
                "employee_rent_payment": self.employee_rent_payment,
                "basic_salary": self.basic_salary,
                "dearness_allowance": self.dearness_allowance,
                "rent_paid_by_employer": self.rent_paid_by_employer,
                "hotel_charges": self.hotel_charges,
                "stay_days": self.stay_days,
                "furniture_cost": self.furniture_cost,
                "furniture_employee_payment": self.furniture_employee_payment,
                "is_furniture_owned_by_employer": self.is_furniture_owned_by_employer
            },
            "car": {
                "car_use_type": self.car_use_type,
                "engine_capacity_cc": self.engine_capacity_cc,
                "months_used": self.months_used,
                "car_cost_to_employer": self.car_cost_to_employer,
                "other_vehicle_cost": self.other_vehicle_cost,
                "has_expense_reimbursement": self.has_expense_reimbursement,
                "driver_provided": self.driver_provided
            },
            "medical_reimbursement": {
                "medical_reimbursement_amount": self.medical_reimbursement_amount,
                "is_overseas_treatment": self.is_overseas_treatment
            },
            "lta": {
                "lta_amount_claimed": self.lta_amount_claimed,
                "lta_claimed_count": self.lta_claimed_count,
                "public_transport_cost": self.public_transport_cost
            },
            "interest_free_loan": {
                "loan_amount": self.loan_amount,
                "outstanding_amount": self.loan_amount,  # Assuming same as loan amount
                "company_interest_rate": self.interest_rate_charged,
                "sbi_interest_rate": self.sbi_rate,
                "loan_months": self.asset_usage_months  # Using asset_usage_months as loan_months
            },
            "esop": {
                "shares_exercised": self.esop_shares_exercised,
                "exercise_price": self.esop_exercise_value,
                "allotment_price": self.esop_fair_market_value
            },
            "utilities": {
                "gas_paid_by_employer": self.gas_electricity_water_amount,
                "electricity_paid_by_employer": 0,
                "water_paid_by_employer": 0,
                "gas_paid_by_employee": 0,
                "electricity_paid_by_employee": 0,
                "water_paid_by_employee": 0,
                "is_gas_manufactured_by_employer": False,
                "is_electricity_manufactured_by_employer": False,
                "is_water_manufactured_by_employer": False
            },
            "free_education": {
                "monthly_expenses_child1": self.free_education_amount if self.is_children_education else 0,
                "monthly_expenses_child2": 0,
                "months_child1": 12 if self.is_children_education else 0,
                "months_child2": 0,
                "employer_maintained_1st_child": self.is_children_education,
                "employer_maintained_2nd_child": False
            },
            "lunch_refreshment": {
                "employer_cost": self.lunch_refreshment_amount,
                "employee_payment": 0,
                "meal_days_per_year": 365
            },
            "domestic_help": {
                "domestic_help_paid_by_employer": self.domestic_help_amount,
                "domestic_help_paid_by_employee": 0
            },
            "movable_asset_usage": {
                "asset_type": "Others",
                "asset_value": self.movable_asset_value,
                "employee_payment": 0,
                "is_employer_owned": True
            },
            "gift_voucher": {
                "gift_voucher_amount": 0
            },
            "monetary_benefits": {
                "monetary_amount_paid_by_employer": 0,
                "expenditure_for_official_purpose": 0,
                "amount_paid_by_employee": 0
            },
            "club_expenses": {
                "club_expenses_paid_by_employer": 0,
                "club_expenses_paid_by_employee": 0,
                "club_expenses_for_official_purpose": 0
            }
        }


# =============================================================================
# HOUSE PROPERTY INCOME DTOs
# =============================================================================

class HousePropertyIncomeDTO(BaseModel):
    """House property income DTO."""
    property_type: str = Field(..., description="Self-Occupied, Let-Out")
    address: str = Field(default="", description="Property address")
    annual_rent_received: Decimal = Field(default=0, ge=0)
    municipal_taxes_paid: Decimal = Field(default=0, ge=0)
    home_loan_interest: Decimal = Field(default=0, ge=0)
    pre_construction_interest: Decimal = Field(default=0, ge=0)
    
    @validator('property_type')
    def validate_property_type(cls, v):
        valid_types = ["Self-Occupied", "Let-Out"]
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
    stcg_111a_equity_stt: Decimal = Field(default=0, ge=0, description="STCG on equity with STT (20%)")
    stcg_other_assets: Decimal = Field(default=0, ge=0, description="STCG on other assets (slab rates)")
    stcg_debt_mf: Decimal = Field(default=0, ge=0, description="STCG on debt mutual funds (slab rates)")
    
    # Long Term Capital Gains
    ltcg_112a_equity_stt: Decimal = Field(default=0, ge=0, description="LTCG on equity with STT (12.5%)")
    ltcg_other_assets: Decimal = Field(default=0, ge=0, description="LTCG on other assets (12.5%)")
    ltcg_debt_mf: Decimal = Field(default=0, ge=0, description="LTCG on debt mutual funds (12.5%)")


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
    post_office_interest: Decimal = Field(default=0, ge=0)
    age: int = Field(default=25, ge=18, le=100)


class OtherIncomeDTO(BaseModel):
    """Other income DTO."""
    interest_income: Optional[InterestIncomeDTO] = None
    house_property_income: Optional[HousePropertyIncomeDTO] = None
    capital_gains_income: Optional[CapitalGainsIncomeDTO] = None
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


class PayoutMonthlyProjectionDTO(BaseModel):
    """Payout monthly projection DTO."""
    employee_id: str = Field(..., description="Employee ID")
    month: int = Field(..., ge=1, le=12, description="Month")
    year: int = Field(..., ge=2020, le=2030, description="Year")
    
    # Salary components
    basic_salary: float = Field(default=0.0, ge=0, description="Basic salary")
    da: float = Field(default=0.0, ge=0, description="Dearness allowance")
    hra: float = Field(default=0.0, ge=0, description="HRA")
    special_allowance: float = Field(default=0.0, ge=0, description="Special allowance")
    bonus: float = Field(default=0.0, ge=0, description="Bonus")
    commission: float = Field(default=0.0, ge=0, description="Commission")
    
    # Deductions
    epf_employee: float = Field(default=0.0, ge=0, description="EPF employee contribution")
    esi_employee: float = Field(default=0.0, ge=0, description="ESI employee contribution")
    professional_tax: float = Field(default=0.0, ge=0, description="Professional tax")
    advance_deduction: float = Field(default=0.0, ge=0, description="Advance deduction")
    loan_deduction: float = Field(default=0.0, ge=0, description="Loan deduction")
    other_deductions: float = Field(default=0.0, ge=0, description="Other deductions")
    
    # Calculated totals
    gross_salary: float = Field(default=0.0, ge=0, description="Gross salary")
    net_salary: float = Field(default=0.0, ge=0, description="Net salary")
    total_deductions: float = Field(default=0.0, ge=0, description="Total deductions")
    tds: float = Field(default=0.0, ge=0, description="TDS")
    
    # Annual projections
    annual_gross_salary: float = Field(default=0.0, ge=0, description="Annual gross salary")
    annual_tax_liability: float = Field(default=0.0, ge=0, description="Annual tax liability")
    
    # Tax details
    tax_regime: str = Field(default="new", description="Tax regime")
    
    # Working days
    effective_working_days: int = Field(default=22, ge=0, description="Effective working days")
    lwp_days: int = Field(default=0, ge=0, description="LWP days")
    
    # Status and notes
    status: str = Field(default="pending", description="Payout status")
    notes: Optional[str] = Field(None, description="Notes")
    remarks: Optional[str] = Field(None, description="Remarks")


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
    monthly_payroll: Optional[PayoutMonthlyProjectionDTO] = None
    
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
    monthly_payroll: Optional[PayoutMonthlyProjectionDTO] = None
    
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


# =============================================================================
# INDIVIDUAL COMPONENT UPDATE DTOs
# =============================================================================

class UpdateSalaryComponentRequest(BaseModel):
    """Request to update salary component individually."""
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    salary_income: SalaryIncomeDTO = Field(..., description="Salary income data")
    force_new_revision: bool = Field(default=False, description="Force create new salary revision instead of updating existing")
    notes: Optional[str] = Field(None, description="Optional notes for the update")


class UpdatePerquisitesComponentRequest(BaseModel):
    """Request to update perquisites component individually."""
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    perquisites: PerquisitesDTO = Field(..., description="Perquisites data")
    notes: Optional[str] = Field(None, description="Optional notes for the update")


class UpdateDeductionsComponentRequest(BaseModel):
    """Request to update deductions component individually."""
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    deductions: TaxDeductionsDTO = Field(..., description="Deductions data")
    notes: Optional[str] = Field(None, description="Optional notes for the update")


class UpdateHousePropertyComponentRequest(BaseModel):
    """Request to update house property component individually."""
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    house_property_income: HousePropertyIncomeDTO = Field(..., description="House property income data")
    notes: Optional[str] = Field(None, description="Optional notes for the update")


class UpdateCapitalGainsComponentRequest(BaseModel):
    """Request to update capital gains component individually."""
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    capital_gains_income: CapitalGainsIncomeDTO = Field(..., description="Capital gains income data")
    notes: Optional[str] = Field(None, description="Optional notes for the update")


class UpdateRetirementBenefitsComponentRequest(BaseModel):
    """Request to update retirement benefits component individually."""
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    retirement_benefits: RetirementBenefitsDTO = Field(..., description="Retirement benefits data")
    notes: Optional[str] = Field(None, description="Optional notes for the update")


class UpdateOtherIncomeComponentRequest(BaseModel):
    """Request to update other income component individually."""
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    other_income: OtherIncomeDTO = Field(..., description="Other income data")
    notes: Optional[str] = Field(None, description="Optional notes for the update")


class UpdateMonthlyPayrollComponentRequest(BaseModel):
    """Request to update monthly payroll component individually."""
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    monthly_payroll: PayoutMonthlyProjectionDTO = Field(..., description="Monthly payroll data")
    notes: Optional[str] = Field(None, description="Optional notes for the update")


class UpdateRegimeComponentRequest(BaseModel):
    """Request to update tax regime component individually."""
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    regime_type: str = Field(..., description="Tax regime: 'old' or 'new'")
    age: int = Field(..., ge=18, le=100, description="Taxpayer age")
    notes: Optional[str] = Field(None, description="Optional notes for the update")
    
    @validator('regime_type')
    def validate_regime(cls, v):
        if v not in ["old", "new"]:
            raise ValueError("Regime must be 'old' or 'new'")
        return v


class ComponentUpdateResponse(BaseModel):
    """Response for individual component updates."""
    taxation_id: str = Field(..., description="Taxation record ID")
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year")
    component_type: str = Field(..., description="Type of component updated")
    status: str = Field(..., description="Update status")
    message: str = Field(..., description="Update message")
    updated_at: datetime = Field(..., description="Update timestamp")
    notes: Optional[str] = Field(None, description="Optional notes")


class GetComponentRequest(BaseModel):
    """Request to get a specific component from taxation record."""
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year (e.g., '2024-25')")
    component_type: str = Field(..., description="Type of component to retrieve")


class ComponentResponse(BaseModel):
    """Response for getting a specific component."""
    taxation_id: str = Field(..., description="Taxation record ID")
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year")
    component_type: str = Field(..., description="Type of component")
    component_data: Dict[str, Any] = Field(..., description="Component data")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    notes: Optional[str] = Field(None, description="Optional notes")


class TaxationRecordStatusResponse(BaseModel):
    """Response showing status of all components in a taxation record."""
    taxation_id: str = Field(..., description="Taxation record ID")
    employee_id: str = Field(..., description="Employee ID")
    tax_year: str = Field(..., description="Tax year")
    regime_type: str = Field(..., description="Tax regime")
    age: int = Field(..., description="Taxpayer age")
    components_status: Dict[str, Dict[str, Any]] = Field(..., description="Status of each component")
    overall_status: str = Field(..., description="Overall record status")
    last_updated: datetime = Field(..., description="Last update timestamp")
    is_final: bool = Field(..., description="Whether record is finalized") 