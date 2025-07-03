"""
Comprehensive Taxation DTOs
Data Transfer Objects for taxation API covering all scenarios including mid-year and periodic calculations
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator, model_validator


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
    children_hostel_count: int = Field(default=0, ge=0)
    hostel_allowance: Decimal = Field(default=0, ge=0)
    underground_mines_allowance: Decimal = Field(default=0, ge=0)
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
    
    # Additional fields from SpecificAllowances that were missing
    hills_exemption_limit: Decimal = Field(default=0, ge=0, description="Hills allowance exemption limit")
    border_exemption_limit: Decimal = Field(default=0, ge=0, description="Border allowance exemption limit")
    children_count: int = Field(default=0, ge=0, description="Number of children for education allowance")
    disabled_transport_allowance: Decimal = Field(default=0, ge=0, description="Disabled transport allowance")
    is_disabled: bool = Field(default=False, description="Whether employee is disabled")
    mine_work_months: int = Field(default=0, ge=0, le=12, description="Underground mines work months")
    fixed_medical_allowance: Decimal = Field(default=0, ge=0, description="Fixed medical allowance")
    any_other_allowance: Decimal = Field(default=0, ge=0, description="Any other allowance (separate from exemption)")
    
    @validator('effective_till')
    def validate_effective_till(cls, v, values):
        if v and 'effective_from' in values and values['effective_from'] and v <= values['effective_from']:
            raise ValueError("effective_till must be after effective_from")
        return v

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
class UpdateSalaryIncomeRequest(BaseModel):
    """Request to update salary income."""
    taxation_id: str = Field(..., description="Taxation record ID")
    salary_income: SalaryIncomeDTO

class UpdateDeductionsRequest(BaseModel):
    """Request to update deductions."""
    taxation_id: str = Field(..., description="Taxation record ID")
    deductions: TaxDeductionsDTO

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

# =============================================================================
# LEGACY RESPONSE DTOs
# =============================================================================

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
    months_used_other_vehicle: int = Field(default=12, ge=0, le=12, description="Months used other vehicle")
    car_cost_to_employer: Decimal = Field(default=0, ge=0, description="Car cost to employer")
    other_vehicle_cost: Decimal = Field(default=0, ge=0, description="Other vehicle cost")
    has_expense_reimbursement: bool = Field(default=False, description="Has expense reimbursement")
    driver_provided: bool = Field(default=False, description="Driver provided")
    
    # LTA fields
    lta_amount_claimed: Decimal = Field(default=0, ge=0, description="LTA amount claimed")
    lta_claimed_count: int = Field(default=0, ge=0, description="LTA claimed count")
    public_transport_cost: Decimal = Field(default=0, ge=0, description="Public transport cost")
    travel_mode: str = Field(default="Air", description="Travel mode: Air, Rail, Bus, Public Transport")
    
    # ESOP fields
    esop_exercise_value: Decimal = Field(default=0, ge=0, description="ESOP exercise value")
    esop_fair_market_value: Decimal = Field(default=0, ge=0, description="ESOP fair market value")
    esop_shares_exercised: int = Field(default=0, ge=0, description="ESOP shares exercised")
    
    # Free education fields - Individual components
    monthly_expenses_child1: Decimal = Field(default=0, ge=0, description="Monthly expenses for 1st child")
    monthly_expenses_child2: Decimal = Field(default=0, ge=0, description="Monthly expenses for 2nd child")
    months_child1: int = Field(default=12, ge=0, le=12, description="Number of months for 1st child")
    months_child2: int = Field(default=12, ge=0, le=12, description="Number of months for 2nd child")
    employer_maintained_1st_child: bool = Field(default=False, description="Is 1st child maintained by employer")
    employer_maintained_2nd_child: bool = Field(default=False, description="Is 2nd child maintained by employer")
    
    # Legacy free education fields for backward compatibility
    free_education_amount: Decimal = Field(default=0, ge=0, description="Free education amount (legacy)")
    is_children_education: bool = Field(default=True, description="Is children education (legacy)")
    
    # Utilities fields - Individual components
    gas_paid_by_employer: Decimal = Field(default=0, ge=0, description="Gas amount paid by employer")
    electricity_paid_by_employer: Decimal = Field(default=0, ge=0, description="Electricity amount paid by employer")
    water_paid_by_employer: Decimal = Field(default=0, ge=0, description="Water amount paid by employer")
    gas_paid_by_employee: Decimal = Field(default=0, ge=0, description="Gas amount paid by employee")
    electricity_paid_by_employee: Decimal = Field(default=0, ge=0, description="Electricity amount paid by employee")
    water_paid_by_employee: Decimal = Field(default=0, ge=0, description="Water amount paid by employee")
    is_gas_manufactured_by_employer: bool = Field(default=False, description="Is gas manufactured by employer")
    is_electricity_manufactured_by_employer: bool = Field(default=False, description="Is electricity manufactured by employer")
    is_water_manufactured_by_employer: bool = Field(default=False, description="Is water manufactured by employer")
    
    # Legacy utilities field for backward compatibility
    gas_electricity_water_amount: Decimal = Field(default=0, ge=0, description="Gas, electricity, water amount (legacy)")
    
    # Interest free loan fields
    loan_amount: Decimal = Field(default=0, ge=0, description="Loan amount")
    emi_amount: Decimal = Field(default=0, ge=0, description="EMI amount")
    company_interest_rate: Decimal = Field(default=0, ge=0, description="Interest rate charged")
    sbi_interest_rate: Decimal = Field(default=6.5, ge=0, description="SBI rate")
    loan_type: str = Field(default="Personal", description="Loan type: Personal, Medical, etc.")
    loan_start_date: Optional[date] = Field(None, description="Loan start date")
    
    # Movable assets fields
    movable_asset_value: Decimal = Field(default=0, ge=0, description="Movable asset value")
    asset_usage_months: int = Field(default=12, ge=0, le=12, description="Asset usage months")
    
    # Lunch refreshment fields - Individual components
    lunch_employer_cost: Decimal = Field(default=0, ge=0, description="Lunch/refreshment cost paid by employer")
    lunch_employee_payment: Decimal = Field(default=0, ge=0, description="Lunch/refreshment payment by employee")
    lunch_meal_days_per_year: int = Field(default=250, ge=0, le=365, description="Number of meal days per year")
    
    # Legacy lunch refreshment field for backward compatibility
    lunch_refreshment_amount: Decimal = Field(default=0, ge=0, description="Lunch refreshment amount (legacy)")
    
    # Domestic help fields - Individual components
    domestic_help_paid_by_employer: Decimal = Field(default=0, ge=0, description="Domestic help cost paid by employer")
    domestic_help_paid_by_employee: Decimal = Field(default=0, ge=0, description="Domestic help payment by employee")
    
    # Movable Asset Usage fields - Individual components
    movable_asset_type: str = Field(default="Electronics", description="Asset type: Electronics, Motor Vehicle, Others")
    movable_asset_usage_value: Decimal = Field(default=0, ge=0, description="Asset value for usage")
    movable_asset_hire_cost: Decimal = Field(default=0, ge=0, description="Hire cost for asset")
    movable_asset_employee_payment: Decimal = Field(default=0, ge=0, description="Employee payment for asset usage")
    movable_asset_is_employer_owned: bool = Field(default=True, description="Is asset owned by employer")
    
    # Movable Asset Transfer fields - Individual components
    movable_asset_transfer_type: str = Field(default="Electronics", description="Asset type for transfer: Electronics, Motor Vehicle, Others")
    movable_asset_transfer_cost: Decimal = Field(default=0, ge=0, description="Original cost of asset for transfer")
    movable_asset_years_of_use: int = Field(default=1, ge=0, le=50, description="Years of use for asset transfer")
    movable_asset_transfer_employee_payment: Decimal = Field(default=0, ge=0, description="Employee payment for asset transfer")
    
    # Other perquisites fields
    other_perquisites_amount: Decimal = Field(default=0, ge=0, description="Other perquisites amount")
    
    # Monetary Benefits fields - Individual components
    monetary_amount_paid_by_employer: Decimal = Field(default=0, ge=0, description="Monetary amount paid by employer")
    expenditure_for_official_purpose: Decimal = Field(default=0, ge=0, description="Expenditure for official purpose")
    amount_paid_by_employee: Decimal = Field(default=0, ge=0, description="Amount paid by employee")
    
    # Club Expenses fields - Individual components
    club_expenses_paid_by_employer: Decimal = Field(default=0, ge=0, description="Club expenses paid by employer")
    club_expenses_paid_by_employee: Decimal = Field(default=0, ge=0, description="Club expenses paid by employee")
    club_expenses_for_official_purpose: Decimal = Field(default=0, ge=0, description="Club expenses for official purpose")
    
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
    
    @validator('travel_mode')
    def validate_travel_mode(cls, v):
        valid_modes = ["Air", "Rail", "Bus", "Public Transport"]
        if v not in valid_modes:
            raise ValueError(f"Travel mode must be one of: {valid_modes}")
        return v
    
    @validator('loan_type')
    def validate_loan_type(cls, v):
        valid_types = ["Personal", "Medical", "Education", "Housing", "Vehicle", "Other"]
        if v not in valid_types:
            raise ValueError(f"Loan type must be one of: {valid_types}")
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
                "months_used_other_vehicle": self.months_used_other_vehicle,
                "car_cost_to_employer": self.car_cost_to_employer,
                "other_vehicle_cost": self.other_vehicle_cost,
                "has_expense_reimbursement": self.has_expense_reimbursement,
                "driver_provided": self.driver_provided
            },
            "lta": {
                "lta_amount_claimed": self.lta_amount_claimed,
                "lta_claimed_count": self.lta_claimed_count,
                "public_transport_cost": self.public_transport_cost,
                "travel_mode": self.travel_mode
            },
            "interest_free_loan": {
                "loan_amount": self.loan_amount,
                "emi_amount": self.emi_amount,
                "outstanding_amount": self.loan_amount,  # Assuming same as loan amount
                "company_interest_rate": self.company_interest_rate,
                "sbi_interest_rate": self.sbi_interest_rate,
                "loan_type": self.loan_type,
                "loan_start_date": self.loan_start_date
            },
            "esop": {
                "shares_exercised": self.esop_shares_exercised,
                "exercise_price": self.esop_exercise_value,
                "allotment_price": self.esop_fair_market_value
            },
            "utilities": {
                "gas_paid_by_employer": self.gas_paid_by_employer,
                "electricity_paid_by_employer": self.electricity_paid_by_employer,
                "water_paid_by_employer": self.water_paid_by_employer,
                "gas_paid_by_employee": self.gas_paid_by_employee,
                "electricity_paid_by_employee": self.electricity_paid_by_employee,
                "water_paid_by_employee": self.water_paid_by_employee,
                "is_gas_manufactured_by_employer": self.is_gas_manufactured_by_employer,
                "is_electricity_manufactured_by_employer": self.is_electricity_manufactured_by_employer,
                "is_water_manufactured_by_employer": self.is_water_manufactured_by_employer
            },
            "free_education": {
                "monthly_expenses_child1": self.monthly_expenses_child1,
                "monthly_expenses_child2": self.monthly_expenses_child2,
                "months_child1": self.months_child1,
                "months_child2": self.months_child2,
                "employer_maintained_1st_child": self.employer_maintained_1st_child,
                "employer_maintained_2nd_child": self.employer_maintained_2nd_child
            },
            "lunch_refreshment": {
                "employer_cost": self.lunch_employer_cost,
                "employee_payment": self.lunch_employee_payment,
                "meal_days_per_year": self.lunch_meal_days_per_year
            },
            "domestic_help": {
                "domestic_help_paid_by_employer": self.domestic_help_paid_by_employer,
                "domestic_help_paid_by_employee": self.domestic_help_paid_by_employee
            },
            "movable_asset_usage": {
                "asset_type": self.movable_asset_type,
                "asset_value": self.movable_asset_usage_value,
                "hire_cost": self.movable_asset_hire_cost,
                "employee_payment": self.movable_asset_employee_payment,
                "is_employer_owned": self.movable_asset_is_employer_owned
            },
            "movable_asset_transfer": {
                "asset_type": self.movable_asset_transfer_type,
                "asset_cost": self.movable_asset_transfer_cost,
                "years_of_use": self.movable_asset_years_of_use,
                "employee_payment": self.movable_asset_transfer_employee_payment
            },
            "gift_voucher": {
                "gift_voucher_amount": 0
            },
            "monetary_benefits": {
                "monetary_amount_paid_by_employer": self.monetary_amount_paid_by_employer,
                "expenditure_for_official_purpose": self.expenditure_for_official_purpose,
                "amount_paid_by_employee": self.amount_paid_by_employee
            },
            "club_expenses": {
                "club_expenses_paid_by_employer": self.club_expenses_paid_by_employer,
                "club_expenses_paid_by_employee": self.club_expenses_paid_by_employee,
                "club_expenses_for_official_purpose": self.club_expenses_for_official_purpose
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
    leave_encashment_amount: Decimal = Field(default=0, ge=0, description="Leave encashment amount received")
    average_monthly_salary: Decimal = Field(default=0, ge=0, description="Average monthly salary for calculation")
    leave_days_encashed: int = Field(default=0, ge=0, description="Number of leave days encashed")
    is_deceased: bool = Field(default=False, description="Whether the employee is deceased")
    during_employment: bool = Field(default=False, description="Whether encashment was during employment")


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
    savings_account_interest: Decimal = Field(default=0, ge=0, alias="savings_interest")
    fixed_deposit_interest: Decimal = Field(default=0, ge=0, alias="fd_interest")
    recurring_deposit_interest: Decimal = Field(default=0, ge=0, alias="rd_interest")
    post_office_interest: Decimal = Field(default=0, ge=0)
    age: int = Field(default=25, ge=18, le=100)
    
    class Config:
        populate_by_name = True


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

class FlatRetirementBenefitsDTO(BaseModel):
    """Flat retirement benefits DTO for frontend compatibility."""
    gratuity_amount: Decimal = Field(default=0, ge=0, description="Gratuity amount")
    leave_encashment_amount: Decimal = Field(default=0, ge=0, description="Leave encashment amount")
    vrs_amount: Decimal = Field(default=0, ge=0, description="VRS amount")
    pension_amount: Decimal = Field(default=0, ge=0, description="Pension amount")
    commuted_pension_amount: Decimal = Field(default=0, ge=0, description="Commuted pension amount")
    other_retirement_benefits: Decimal = Field(default=0, ge=0, description="Other retirement benefits")
    
    def to_nested_structure(self) -> RetirementBenefitsDTO:
        """Convert flat structure to nested structure."""
        return RetirementBenefitsDTO(
            gratuity=GratuityDTO(
                gratuity_amount=self.gratuity_amount,
                monthly_salary=Decimal(0),
                service_years=Decimal(0),
                is_govt_employee=False
            ) if self.gratuity_amount > 0 else None,
            leave_encashment=LeaveEncashmentDTO(
                leave_encashment_amount=self.leave_encashment_amount,
                average_monthly_salary=Decimal(0),
                leave_days_encashed=0,
                is_govt_employee=False,
                during_employment=False
            ) if self.leave_encashment_amount > 0 else None,
            vrs=VRSDTO(
                vrs_amount=self.vrs_amount,
                monthly_salary=Decimal(0),
                service_years=Decimal(0)
            ) if self.vrs_amount > 0 else None,
            pension=PensionDTO(
                regular_pension=self.pension_amount,
                commuted_pension=self.commuted_pension_amount,
                total_pension=self.pension_amount + self.commuted_pension_amount,
                is_govt_employee=False,
                gratuity_received=False
            ) if (self.pension_amount > 0 or self.commuted_pension_amount > 0) else None,
            retrenchment_compensation=RetrenchmentCompensationDTO(
                retrenchment_amount=self.other_retirement_benefits,
                monthly_salary=Decimal(0),
                service_years=Decimal(0)
            ) if self.other_retirement_benefits > 0 else None
        )


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
    retirement_benefits: Union[RetirementBenefitsDTO, FlatRetirementBenefitsDTO] = Field(..., description="Retirement benefits data")
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