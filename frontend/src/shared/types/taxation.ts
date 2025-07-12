// Backend-aligned taxation types - Direct match with backend DTOs
// Based on TAXATION_FIELD_MAPPING_SUMMARY.md

export interface SalaryIncomeDTO {
  basic_salary: number;
  dearness_allowance: number;
  hra_provided: number;
  pf_employee_contribution: number;
  pf_employer_contribution: number;
  esi_contribution: number;
  pf_voluntary_contribution: number;
  special_allowance: number;
  bonus: number;
  commission: number;
  conveyance_allowance: number;
  medical_allowance: number;
  other_allowances: number;
  // Additional detailed allowances from backend
  city_compensatory_allowance?: number;
  rural_allowance?: number;
  proctorship_allowance?: number;
  wardenship_allowance?: number;
  project_allowance?: number;
  deputation_allowance?: number;
  interim_relief?: number;
  tiffin_allowance?: number;
  overtime_allowance?: number;
  servant_allowance?: number;
  hills_high_altd_allowance?: number;
  hills_high_altd_exemption_limit?: number;
  border_remote_allowance?: number;
  border_remote_exemption_limit?: number;
  transport_employee_allowance?: number;
  children_education_allowance?: number;
  children_education_count?: number;
  children_hostel_count?: number;
  hostel_allowance?: number;
  underground_mines_allowance?: number;
  govt_employee_entertainment_allowance?: number;
  govt_employees_outside_india_allowance?: number;
  supreme_high_court_judges_allowance?: number;
  judge_compensatory_allowance?: number;
  section_10_14_special_allowances?: number;
  travel_on_tour_allowance?: number;
  tour_daily_charge_allowance?: number;
  conveyance_in_performace_of_duties?: number;
  helper_in_performace_of_duties?: number;
  academic_research?: number;
  uniform_allowance?: number;
  any_other_allowance_exemption?: number;
  
  // Additional fields from SpecificAllowances that were missing
  hills_exemption_limit?: number;
  border_exemption_limit?: number;
  children_count?: number;
  disabled_transport_allowance?: number;
  is_disabled?: boolean;
  mine_work_months?: number;
  fixed_medical_allowance?: number;
  any_other_allowance?: number;
  
  // Effective date fields for salary revisions
  effective_from?: string;
  effective_till?: string;
}

export interface OtherIncomeDTO {
  interest_income: {
    savings_account_interest: number;
    fixed_deposit_interest: number;
    recurring_deposit_interest?: number;
    post_office_interest?: number;
  };
  dividend_income: number;
  gifts_received: number;
  business_professional_income?: number;
  other_miscellaneous_income: number;
  house_property_income?: {
    property_type: string;
    address: string;
    annual_rent_received: number;
    municipal_taxes_paid: number;
    home_loan_interest: number;
    pre_construction_interest: number;
  };
}

export interface CapitalGainsIncomeDTO {
  stcg_111a_equity_stt: number;
  stcg_other_assets: number;
  stcg_debt_mf: number;
  ltcg_112a_equity_stt: number;
  ltcg_other_assets: number;
  ltcg_debt_mf: number;
}

export interface HousePropertyIncomeDTO {
  annual_rent: number;
  municipal_taxes_paid: number;
  standard_deduction: number;
  interest_on_loan: number;
  net_income: number;
  property_address?: string;
  occupancy_status?: string;
  pre_construction_loan_interest?: number;
}

export interface HRAExemptionDTO {
  actual_rent_paid: number;
  hra_city_type: 'metro' | 'non_metro';
}

export interface TaxDeductionsDTO {
  hra_exemption?: HRAExemptionDTO;
  section_80c: {
    life_insurance_premium: number;
    nsc_investment: number;
    tax_saving_fd: number;
    elss_investment: number;
    home_loan_principal: number;
    tuition_fees: number;
    ulip_premium: number;
    sukanya_samriddhi: number;
    stamp_duty_property: number;
    senior_citizen_savings: number;
    other_80c_investments: number;
  };
  section_80ccc: {
    pension_fund_contribution: number;
  };
  section_80ccd: {
    employee_nps_contribution: number;
    additional_nps_contribution: number;
    employer_nps_contribution: number;
  };
  section_80d: {
    self_family_premium: number;
    parent_premium: number;
    preventive_health_checkup: number;
    employee_age: number;
    parent_age: number;
  };
  section_80dd: {
    relation: string;
    disability_percentage: string;
  };
  section_80ddb: {
    dependent_age: number;
    medical_expenses: number;
    relation: string;
  };
  section_80e: {
    education_loan_interest: number;
    relation: string;
  };
  section_80eeb: {
    ev_loan_interest: number;
    ev_purchase_date: string;
  };
  section_80g: {
    // 100% deduction without qualifying limit
    pm_relief_fund: number;
    national_defence_fund: number;
    national_foundation_communal_harmony: number;
    zila_saksharta_samiti: number;
    national_illness_assistance_fund: number;
    national_blood_transfusion_council: number;
    national_trust_autism_fund: number;
    national_sports_fund: number;
    national_cultural_fund: number;
    technology_development_fund: number;
    national_children_fund: number;
    cm_relief_fund: number;
    army_naval_air_force_funds: number;
    swachh_bharat_kosh: number;
    clean_ganga_fund: number;
    drug_abuse_control_fund: number;
    other_100_percent_wo_limit: number;
    
    // 50% deduction without qualifying limit
    jn_memorial_fund: number;
    pm_drought_relief: number;
    indira_gandhi_memorial_trust: number;
    rajiv_gandhi_foundation: number;
    other_50_percent_wo_limit: number;
    
    // 100% deduction with qualifying limit
    family_planning_donation: number;
    indian_olympic_association: number;
    other_100_percent_w_limit: number;
    
    // 50% deduction with qualifying limit
    govt_charitable_donations: number;
    housing_authorities_donations: number;
    religious_renovation_donations: number;
    other_charitable_donations: number;
    other_50_percent_w_limit: number;
  };
  section_80ggc: {
    political_party_contribution: number;
  };
  section_80u: {
    disability_percentage: string;
  };
  section_80tta_ttb: {
    savings_interest: number;
    fd_interest: number;
    rd_interest: number;
    post_office_interest: number;
    age: number;
  };
}

export interface RetirementBenefitsDTO {
  leave_encashment?: {
    leave_encashment_income_received: number;
    leave_encashment_exemption: number;
    leave_encashment_taxable: number;
    is_deceased?: boolean;
    during_employment?: boolean;
  };
  pension?: {
    pension_received: number;
    commuted_pension: number;
    uncommuted_pension: number;
    computed_pension_percentage?: number;
    uncomputed_pension_frequency?: string;
    uncomputed_pension_amount?: number;
  };
  vrs?: {
    compensation_received: number;
    exemption_limit: number;
    taxable_amount: number;
    is_vrs_requested?: boolean;
  };
  gratuity?: {
    gratuity_received: number;
    exemption_limit: number;
    taxable_amount: number;
  };
  retrenchment_compensation?: {
    compensation_received: number;
    exemption_limit: number;
    taxable_amount: number;
    is_provided?: boolean;
  };
}

export interface PerquisitesDTO {
  accommodation?: {
    accommodation_type: 'company_owned' | 'company_leased' | 'none';
    accommodation_value: number;
    accommodation_govt_lic_fees?: number;
    accommodation_city_population?: string;
    accommodation_rent?: number;
    is_furniture_owned?: boolean;
    furniture_actual_cost?: number;
  };
  car_transport?: {
    car_provided: boolean;
    car_cc: number;
    car_owned_by: 'company' | 'employee';
    car_used_for_business: number;
    car_value: number;
    driver_salary: number;
    driver_cost: number;
    fuel_provided: boolean;
    fuel_value: number;
  };
  gas_electricity_water?: {
    amount: number;
  };
  leave_travel_allowance?: {
    lta_allocated_yearly: number;
    lta_claimed: number;
    lta_exempt: number;
    travel_mode?: string;
    is_monthly_paid?: boolean;
  };
  free_education?: {
    education_provided: boolean;
    education_value: number;
  };
  loans?: {
    loan_amount: number;
    loan_interest_rate: number;
    loan_interest_benefit: number;
  };
  movable_assets?: {
    movable_assets_value: number;
    mau_ownership?: string;
    mau_value_to_employer?: number;
    mau_value_to_employee?: number;
    mat_type?: string;
    mat_value_to_employer?: number;
    mat_value_to_employee?: number;
    mat_number_of_completed_years_of_use?: number;
  };
  esop_stock_options?: {
    esop_value: number;
    esop_exercise_price: number;
    esop_market_price: number;
  };
  other_perquisites?: {
    domestic_help_amount_paid_by_employer?: number;
    domestic_help_amount_paid_by_employee?: number;
    gardener_amount_paid_by_employer?: number;
    sweeper_amount_paid_by_employer?: number;
    personal_attendant_amount_paid_by_employer?: number;
    security_amount_paid_by_employer?: number;
    watchman_amount_paid_by_employer?: number;
    credit_card_amount_paid_by_employer?: number;
    club_expenses_amount_paid_by_employer?: number;
    club_expenses_amount_paid_by_employee?: number;
    use_of_movable_assets_amount_paid_by_employer?: number;
    transfer_of_movable_assets_amount_paid_by_employer?: number;
    interest_free_loan_amount_paid_by_employer?: number;
    club_expenses_amount_paid_for_offical_purpose?: number;
    lunch_amount_paid_by_employer?: number;
    lunch_amount_paid_by_employee?: number;
    monetary_amount_paid_by_employer?: number;
    expenditure_for_offical_purpose?: number;
    monetary_benefits_amount_paid_by_employee?: number;
    gift_vouchers_amount_paid_by_employer?: number;
    total_perquisites: number;
  };
}

// Main TaxationData interface - backend aligned
export interface TaxationData {
  employee_id: string;
  tax_year: string;
  regime: 'old' | 'new';
  age: number;
  salary_income: SalaryIncomeDTO;
  other_income: OtherIncomeDTO;
  capital_gains_income: CapitalGainsIncomeDTO;
  house_property_income: HousePropertyIncomeDTO;
  deductions: TaxDeductionsDTO;
  retirement_benefits: RetirementBenefitsDTO;
  perquisites: PerquisitesDTO;
  is_govt_employee?: boolean;
}

// API Response types
export interface TaxationRecord extends TaxationData {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface TaxCalculationResult {
  gross_total_income: number;
  total_deductions: number;
  taxable_income: number;
  tax_before_rebate: number;
  rebate_under_87a: number;
  tax_after_rebate: number;
  health_education_cess: number;
  total_tax_liability: number;
}

// Comprehensive Tax Calculation Response from backend
export interface ComprehensiveTaxCalculationResponse {
  total_income: {
    amount: string;
    currency: string;
  };
  total_exemptions: {
    amount: string;
    currency: string;
  };
  total_deductions: {
    amount: string;
    currency: string;
  };
  taxable_income: {
    amount: string;
    currency: string;
  };
  tax_liability: {
    amount: string;
    currency: string;
  };
  
  // Additional fields returned by the backend
  total_tax_liability?: any;
  effective_tax_rate?: number;
  regime_used?: string;
  gross_income?: any;
  tax_before_rebate?: number;
  rebate_87a?: number;
  tax_after_rebate?: number;
  surcharge?: number;
  cess?: number;
  employment_periods?: any;
  total_employment_days?: number;
  is_mid_year_scenario?: boolean;
  period_wise_income?: any;
  surcharge_breakdown?: any;
  full_year_projection?: any;
  mid_year_impact?: any;
  optimization_suggestions?: any;
  taxpayer_age?: number;
  calculation_breakdown?: any;
  message?: string;
  monthly_payroll?: any;
  
  tax_breakdown: {
    income_breakdown: {
      salary_income: {
        basic_salary: number;
        dearness_allowance: number;
        hra_provided: number;
        special_allowance: number;
        conveyance_allowance: number;
        medical_allowance: number;
        bonus: number;
        commission: number;
        other_allowances: number;
      };
      perquisites: {
        car_perquisite: number;
        driver_perquisite: number;
        fuel_perquisite: number;
        education_perquisite: number;
        domestic_servant_perquisite: number;
        utility_perquisite: number;
        loan_perquisite: number;
        esop_perquisite: number;
        club_membership_perquisite: number;
        other_perquisites: number;
      };
      house_property_income: {
        property_type: string;
        annual_rent_received: number;
        municipal_taxes_paid: number;
        interest_on_loan: number;
        pre_construction_interest: number;
        other_deductions: number;
      };
      capital_gains_income: {
        stcg_111a_equity_stt: number;
        stcg_other_assets: number;
        stcg_debt_mf: number;
        ltcg_112a_equity_stt: number;
        ltcg_other_assets: number;
        ltcg_debt_mf: number;
      };
      retirement_benefits: {
        gratuity_amount: number;
        years_of_service: number;
        is_government_employee: boolean;
        leave_encashment_amount: number;
        leave_balance: number;
        pension_amount: number;
        is_commuted_pension: boolean;
        commutation_percentage: number;
        vrs_compensation: number;
        other_retirement_benefits: number;
      };
      other_income: {
        bank_interest: number;
        fixed_deposit_interest: number;
        recurring_deposit_interest: number;
        post_office_interest: number;
        equity_dividend: number;
        mutual_fund_dividend: number;
        other_dividend: number;
        house_property_rent: number;
        commercial_property_rent: number;
        other_rental: number;
        business_income: number;
        professional_income: number;
        short_term_capital_gains: number;
        long_term_capital_gains: number;
        lottery_winnings: number;
        horse_race_winnings: number;
        crossword_puzzle_winnings: number;
        card_game_winnings: number;
        other_speculative_income: number;
        agricultural_income: number;
        share_of_profit_partnership: number;
        interest_on_tax_free_bonds: number;
        other_exempt_income: number;
      };
    };
    exemptions_breakdown: {
      hra_exemption: number;
      gratuity_exemption: number;
      leave_encashment_exemption: number;
      pension_exemption: number;
      vrs_exemption: number;
      other_exemptions: number;
    };
    deductions_breakdown: {
      section_80c: number;
      section_80d: number;
      section_80e: number;
      section_80g: number;
      section_80tta: number;
      section_80ttb: number;
      section_80u: number;
      other_deductions: number;
    };
    tax_summary: {
      total_income: number;
      total_exemptions: number;
      total_deductions: number;
      taxable_income: number;
      tax_liability: number;
      regime: string;
    };
  };
  regime_comparison: any | null;
}

export interface TaxationResponse {
  taxation_record: TaxationRecord;
  tax_calculation: TaxCalculationResult;
}

// Additional types for compatibility
export type TaxRegime = 'old' | 'new';
export type FilingStatus = 'not_filed' | 'filed' | 'processed' | 'verified' | 'draft' | 'submitted' | 'approved' | 'rejected' | 'pending';

export interface TaxationListResponse {
  records: TaxationData[];
  total: number;
  page: number;
  limit: number;
  message: string;
  success: boolean;
}

// Component Response Interface
export interface ComponentResponse {
  taxation_id: string;
  employee_id: string;
  tax_year: string;
  component_type: string;
  component_data: Record<string, any>;
  last_updated?: string;
  notes?: string;
}

export interface ComponentUpdateResponse {
  taxation_id: string;
  employee_id: string;
  tax_year: string;
  component_type: string;
  status: string;
  message: string;
  updated_at: string;
  notes?: string;
}

export interface TaxationRecordStatusResponse {
  taxation_id: string;
  employee_id: string;
  tax_year: string;
  regime_type: string;
  age: number;
  components_status: Record<string, {
    has_data: boolean;
    last_updated?: string;
    status: string;
    [key: string]: any;
  }>;
  overall_status: string;
  last_updated: string;
  is_final: boolean;
} 