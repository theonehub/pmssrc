// =============================================================================
// COMPREHENSIVE TAXATION API TYPES
// TypeScript definitions for backend DTOs and API responses
// =============================================================================

// Base types
export type TaxRegime = 'old' | 'new';
export type FilingStatus = 'pending' | 'filed' | 'reviewed' | 'finalized';
export type IncomeType = 'salary' | 'house_property_income' | 'capital_gains' | 'other';

// =============================================================================
// COMPREHENSIVE TAX INPUT DTO
// =============================================================================

export interface SalaryIncomeDTO {
  basic_salary: number;
  hra: number;
  special_allowance: number;
  other_allowances: number;
  bonus: number;
  commission: number;
  overtime: number;
  arrears: number;
  gratuity: number;
  leave_encashment: number;
  professional_tax: number;
  tds_deducted: number;
  employer_pf: number;
  employee_pf: number;
  employer_esic: number;
  employee_esic: number;
  lta: number;
  medical_allowance: number;
  conveyance_allowance: number;
  food_allowance: number;
  telephone_allowance: number;
  uniform_allowance: number;
  educational_allowance: number;
}

export interface PerquisitesDTO {
  accommodation_value: number;
  car_benefit: number;
  driver_salary: number;
  fuel_benefit: number;
  telephone_benefit: number;
  club_benefit: number;
  credit_card_benefit: number;
  loan_benefit: number;
  insurance_benefit: number;
  gift_benefit: number;
  meal_benefit: number;
  recreational_benefit: number;
  medical_benefit: number;
  education_benefit: number;
  stock_option_benefit: number;
  other_benefits: number;
}

export interface HousePropertyIncomeDTO {
  property_type: 'self_occupied' | 'let_out' | 'deemed_let_out';
  annual_rent_received: number;
  municipal_tax_paid: number;
  standard_deduction_rate: number;
  interest_on_loan: number;
  pre_construction_interest: number;
  other_expenses: number;
  vacancy_period_months: number;
  co_owner_share_percentage: number;
}

export interface MultipleHousePropertiesDTO {
  properties: HousePropertyIncomeDTO[];
}

export interface CapitalGainsIncomeDTO {
  short_term_gains: number;
  long_term_gains: number;
  stcg_on_equity: number;
  ltcg_on_equity: number;
  stcg_on_property: number;
  ltcg_on_property: number;
  stcg_on_other_assets: number;
  ltcg_on_other_assets: number;
  indexation_benefit: number;
}

export interface RetirementBenefitsDTO {
  provident_fund: number;
  gratuity: number;
  pension: number;
  commuted_pension: number;
  leave_encashment: number;
  voluntary_retirement: number;
  retrenchment_compensation: number;
}

export interface OtherIncomeDTO {
  interest_from_deposits: number;
  interest_from_bonds: number;
  dividend_income: number;
  lottery_winnings: number;
  gambling_winnings: number;
  gift_received: number;
  professional_income: number;
  business_income: number;
  rental_income_other: number;
  royalty_income: number;
  foreign_income: number;
  digital_asset_income: number;
  house_property_income?: {
    property_type: string;
    address: string;
    annual_rent_received: number;
    municipal_taxes_paid: number;
    home_loan_interest: number;
    pre_construction_interest: number;
  };
}

export interface DeductionsDTO {
  section_80c: number;
  section_80ccc: number;
  section_80ccd_1: number;
  section_80ccd_1b: number;
  section_80ccd_2: number;
  section_80d_self: number;
  section_80d_parents: number;
  section_80dd: number;
  section_80ddb: number;
  section_80e: number;
  section_80ee: number;
  section_80eea: number;
  section_80eeb: number;
  section_80g: number;
  section_80gga: number;
  section_80ggc: number;
  section_80ia: number;
  section_80ib: number;
  section_80ic: number;
  section_80id: number;
  section_80ie: number;
  section_80jjaa: number;
  section_80tta: number;
  section_80ttb: number;
  section_80u: number;
}

export interface ComprehensiveTaxInputDTO {
  tax_year: string;
  regime_type: TaxRegime;
  age: number;
  residential_status: 'resident' | 'non_resident' | 'not_ordinarily_resident';
  
  // Income sources
  salary_income?: SalaryIncomeDTO;
  perquisites?: PerquisitesDTO;
  house_property_income?: HousePropertyIncomeDTO;
  multiple_house_properties?: MultipleHousePropertiesDTO;
  capital_gains?: CapitalGainsIncomeDTO;
  retirement_benefits?: RetirementBenefitsDTO;
  other_income?: OtherIncomeDTO;
  
  // Deductions
  deductions?: DeductionsDTO;
  
  // Additional fields
  previous_employer_salary?: number;
  previous_employer_tds?: number;
  advance_tax_paid?: number;
  self_assessment_tax?: number;
}

// =============================================================================
// TAX CALCULATION RESPONSE DTO
// =============================================================================

export interface TaxBreakdownDTO {
  regime_type: TaxRegime;
  gross_total_income: number;
  total_deductions: number;
  taxable_income: number;
  income_tax: number;
  surcharge: number;
  education_cess: number;
  total_tax_liability: number;
  tds_deducted: number;
  advance_tax_paid: number;
  self_assessment_tax: number;
  refund_due: number;
  additional_tax_due: number;
  effective_tax_rate: number;
  average_tax_rate: number;
  marginal_tax_rate: number;
}

export interface IncomeBreakdownDTO {
  salary_income: number;
  house_property_income: number;
  capital_gains_income: number;
  other_income: number;
  total_income: number;
}

export interface DeductionBreakdownDTO {
  standard_deduction: number;
  section_80c: number;
  section_80d: number;
  other_deductions: number;
  total_deductions: number;
}

export interface TaxSlabDTO {
  range_start: number;
  range_end: number | null;
  rate: number;
  tax_amount: number;
}

export interface MonthlyProjectionDTO {
  month: string;
  projected_income: number;
  projected_tax: number;
  cumulative_income: number;
  cumulative_tax: number;
}

export interface PeriodicTaxCalculationResponseDTO {
  calculation_id: string;
  tax_year: string;
  regime_type: TaxRegime;
  calculated_at: string;
  
  // Main calculation results
  tax_breakdown: TaxBreakdownDTO;
  income_breakdown: IncomeBreakdownDTO;
  deduction_breakdown: DeductionBreakdownDTO;
  tax_slabs: TaxSlabDTO[];
  
  // Projections and comparisons
  monthly_projections: MonthlyProjectionDTO[];
  regime_comparison?: RegimeComparisonDTO;
  
  // Recommendations
  tax_saving_suggestions: TaxSavingSuggestionDTO[];
  optimization_opportunities: OptimizationOpportunityDTO[];
}

export interface RegimeComparisonDTO {
  old_regime: TaxBreakdownDTO;
  new_regime: TaxBreakdownDTO;
  recommended_regime: TaxRegime;
  savings_amount: number;
  savings_percentage: number;
}

export interface TaxSavingSuggestionDTO {
  section: string;
  current_amount: number;
  maximum_limit: number;
  additional_investment: number;
  tax_savings: number;
  roi_equivalent: number;
}

export interface OptimizationOpportunityDTO {
  opportunity_type: string;
  description: string;
  potential_savings: number;
  action_required: string;
  priority: 'high' | 'medium' | 'low';
}

// =============================================================================
// SCENARIO CALCULATION DTOs
// =============================================================================

export interface MidYearJoinerDTO {
  joining_date: string;
  current_employer_salary: SalaryIncomeDTO;
  previous_employer_salary?: SalaryIncomeDTO;
  previous_employer_tds?: number;
  months_worked: number;
  projected_annual_salary: number;
}

export interface MidYearIncrementDTO {
  increment_date: string;
  old_salary: SalaryIncomeDTO;
  new_salary: SalaryIncomeDTO;
  increment_percentage: number;
  arrears_amount: number;
}

export interface ScenarioComparisonRequestDTO {
  base_scenario: ComprehensiveTaxInputDTO;
  alternative_scenarios: ComprehensiveTaxInputDTO[];
  scenario_names: string[];
}

export interface ScenarioComparisonResponseDTO {
  base_scenario_result: PeriodicTaxCalculationResponseDTO;
  alternative_results: PeriodicTaxCalculationResponseDTO[];
  comparison_summary: ScenarioComparisonSummaryDTO[];
}

export interface ScenarioComparisonSummaryDTO {
  scenario_name: string;
  tax_liability: number;
  difference_from_base: number;
  percentage_difference: number;
  recommended: boolean;
}

// =============================================================================
// UTILITY AND INFORMATION DTOs
// =============================================================================

export interface TaxRegimeInfoDTO {
  regime_type: TaxRegime;
  description: string;
  deductions_available: boolean;
  exemptions_available: boolean;
  standard_deduction: number;
  popular_sections: string[];
}

export interface TaxSlabInfoDTO {
  range: string;
  rate: string;
  applicable_regimes: TaxRegime[];
}

export interface TaxYearInfoDTO {
  value: string;
  display_name: string;
  assessment_year: string;
  is_current: boolean;
}

// =============================================================================
// API ERROR TYPES
// =============================================================================

export interface ApiErrorResponse {
  detail: string;
  code?: string;
  timestamp: string;
  path?: string;
}

export interface ValidationErrorResponse {
  detail: string;
  validation_errors: Array<{
    field: string;
    message: string;
    code: string;
  }>;
}

// =============================================================================
// COMMON TYPES
// =============================================================================

export interface PaginationParams {
  page?: number;
  limit?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  features: string[];
  timestamp: string;
}

// =============================================================================
// EMPLOYEE SELECTION TYPES
// =============================================================================

export interface CalculationDetails {
  annual_gross_income: number;
  annual_exemptions: number;
  annual_deductions: number;
  annual_taxable_income: number;
  annual_tax_liability: number;
  effective_tax_rate: number;
  tax_regime: string;
  last_calculated_at: string;
  // Add other fields as needed from backend
}

export interface EmployeeSelectionDTO {
  employee_id: string;
  user_name: string;
  email: string;
  department?: string;
  role?: string;
  status?: string;
  joining_date?: string;
  current_salary?: number;
  has_tax_record: boolean;
  tax_year?: string;
  filing_status?: string;
  total_tax?: number;
  regime?: string;
  last_updated?: string;
  calculation_details?: CalculationDetails; // <-- Added for annual_tax_liability
}

export interface EmployeeSelectionQuery {
  skip?: number;
  limit?: number;
  search?: string;
  department?: string;
  role?: string;
  status?: string;
  has_tax_record?: boolean;
  tax_year?: string;
}

export interface EmployeeSelectionResponse {
  total: number;
  employees: EmployeeSelectionDTO[];
  skip: number;
  limit: number;
  has_more: boolean;
}

// =============================================================================
// INDIVIDUAL COMPONENT MANAGEMENT TYPES
// =============================================================================

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