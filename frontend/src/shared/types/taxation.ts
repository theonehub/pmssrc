// Backend-aligned taxation types - Direct match with backend DTOs
// Based on TAXATION_FIELD_MAPPING_SUMMARY.md

export interface SalaryIncomeDTO {
  basic_salary: number;
  dearness_allowance: number;
  hra_received: number;
  hra_city_type: 'metro' | 'non_metro';
  actual_rent_paid: number;
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
  children_education_months?: number;
  hostel_allowance?: number;
  hostel_count?: number;
  hostel_months?: number;
  transport_months?: number;
  underground_mines_allowance?: number;
  underground_mines_months?: number;
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
}

export interface OtherIncomeDTO {
  interest_income: {
    savings_account_interest: number;
    fixed_deposit_interest: number;
    recurring_deposit_interest?: number;
    other_interest?: number;
  };
  dividend_income: number;
  gifts_received: number;
  business_professional_income?: number;
  other_miscellaneous_income: number;
}

export interface CapitalGainsIncomeDTO {
  stcg_111a_equity_stt: number;
  stcg_other_assets: number;
  stcg_debt_mutual_fund?: number;
  ltcg_112a_equity_stt: number;
  ltcg_other_assets?: number;
  ltcg_debt_mf: number;
}

export interface HousePropertyIncomeDTO {
  annual_rent: number;
  municipal_tax: number;
  standard_deduction: number;
  interest_on_loan: number;
  net_income: number;
  property_address?: string;
  occupancy_status?: string;
  pre_construction_loan_interest?: number;
}

export interface TaxDeductionsDTO {
  section_80c: {
    life_insurance_premium: number;
    epf_contribution: number;
    ssp_contribution?: number;
    nsc_investment: number;
    ulip_investment?: number;
    tax_saver_mutual_fund?: number;
    tuition_fees_for_two_children?: number;
    principal_amount_paid_home_loan?: number;
    sukanya_deposit_plan_for_girl_child?: number;
    tax_saver_fixed_deposit_5_years_bank?: number;
    senior_citizen_savings_scheme?: number;
    others?: number;
  };
  section_80ccc: {
    pension_plan_insurance_company?: number;
  };
  section_80ccd: {
    nps_contribution_10_percent?: number;
    additional_nps_50k?: number;
    employer_nps_contribution?: number;
  };
  section_80d: {
    self_family_premium: number;
    preventive_health_checkup_self?: number;
    parent_premium: number;
  };
  section_80dd: {
    amount?: number;
    relation?: string;
    disability_percentage?: string;
  };
  section_80ddb: {
    amount?: number;
    relation?: string;
  };
  section_80e: {
    education_loan_interest: number;
  };
  section_80eeb?: {
    amount?: number;
  };
  section_80g: {
    donation_100_percent_without_limit?: number;
    donation_50_percent_without_limit?: number;
    donation_100_percent_with_limit?: number;
    donation_50_percent_with_limit?: number;
  };
  section_80ggc?: {
    amount?: number;
  };
  section_80u?: {
    amount?: number;
    disability_percentage?: string;
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
    fuel_provided: boolean;
    fuel_value: number;
  };
  gas_electricity_water?: {
    amount: number;
  };
  medical_reimbursement?: {
    amount: number;
  };
  leave_travel_allowance?: {
    lta_claimed: number;
    lta_exempt: number;
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
        hra_received: number;
        special_allowance: number;
        conveyance_allowance: number;
        medical_allowance: number;
        bonus: number;
        commission: number;
        other_allowances: number;
      };
      perquisites: {
        rent_free_accommodation: number;
        concessional_accommodation: number;
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
        fair_rental_value: number;
        standard_rent: number;
        actual_rent: number;
        municipal_tax: number;
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
        other_interest: number;
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