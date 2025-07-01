// Authentication types
export interface LoginCredentials {
  email?: string;
  username?: string;
  password: string;
  hostname?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
  user_info?: User; // Additional property for compatibility
  permissions?: string[]; // Additional property for compatibility
}

export interface TokenData {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  // JWT fields for compatibility
  sub?: string;
  username?: string;
  employee_id?: string;
  role?: UserRole;
  hostname?: string;
  permissions?: string[];
  iat?: number;
  exp?: number;
  type?: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  employee_id?: string;
  department?: string;
  designation?: string;
  mobile?: string;
  gender?: string;
  date_of_joining?: string;
  date_of_birth?: string;
  address?: string;
  phone?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  position?: string;
}

export interface UserListResponse {
  users?: User[];
  total?: number;
  page?: number;
  limit?: number;
  data?: User[]; // Primary data property for API responses
}

export interface CreateUserRequest {
  email: string;
  name: string;
  role: UserRole;
  employee_id?: string;
  department?: string;
  designation?: string;
  mobile?: string;
  gender?: string;
  date_of_joining?: string;
  date_of_birth?: string;
  address?: string;
  phone?: string;
}

export interface UserFiles {
  profile_picture?: File;
  documents?: FileList | File[];
}

export interface UserFilters {
  role?: UserRole;
  department?: string;
  status?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

export type UserRole = 'admin' | 'hr' | 'employee' | 'manager' | 'superadmin' | 'user';

// Import taxation types from dedicated file
export * from './taxation';

export interface Perquisites {
  // Accommodation
  accommodation_type?: 'company_owned' | 'company_leased' | 'none';
  accommodation_provided?: string; // Additional property for compatibility
  accommodation_value?: number;
  accommodation_govt_lic_fees?: number; // Add missing property
  accommodation_city_population?: string; // Add missing property
  accommodation_rent?: number; // Add missing property
  is_furniture_owned?: boolean; // Add missing property
  furniture_actual_cost?: number; // Add missing property
  
  // Car and transport
  car_provided: boolean;
  car_cc: number;
  car_owned_by: 'company' | 'employee';
  car_used_for_business: number; // percentage
  car_value: number;
  driver_salary: number;
  fuel_provided: boolean;
  fuel_value: number;
  
  // Gas, electricity, water
  gas_electricity_water: number;
  
  // Leave travel allowance
  lta_claimed: number;
  lta_exempt: number;
  travel_mode?: string;
  
  // Free education
  education_provided: boolean;
  education_value: number;
  
  // Loans
  loan_amount: number;
  loan_interest_rate: number;
  loan_interest_benefit: number;
  
  // Movable assets
  movable_assets_value: number;
  
  // ESOP/Stock options
  esop_value: number;
  esop_exercise_price: number;
  esop_market_price: number;
  
  // Other perquisites
  other_perquisites: number;
  
  // Total
  total_perquisites: number;
  
  // Additional movable assets properties
  mau_ownership?: string;
  mau_value_to_employer?: number;
  mau_value_to_employee?: number;
  mat_type?: string;
  mat_value_to_employer?: number;
  mat_value_to_employee?: number;
  mat_number_of_completed_years_of_use?: number;
  
  // Additional other perquisites properties
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
}

export type TaxRegime = 'old' | 'new';
export type FilingStatus = 'not_filed' | 'filed' | 'processed' | 'verified' | 'draft' | 'submitted' | 'approved' | 'rejected' | 'pending';

// Tax breakup interface for compatibility
export interface TaxBreakup {
  gross_total_income: number;
  total_deductions: number;
  taxable_income: number;
  tax_before_relief: number;
  tax_relief: number;
  tax_payable: number;
  details?: Record<string, number>;
}

// Extended taxation data for detailed views
export interface ExtendedTaxBreakup {
  basic_salary: number;
  hra: number;
  da: number;
  medical_allowance: number;
  transport_allowance: number;
  other_allowances: number;
  bonus: number;
  perquisites: number;
  other_income: number;
  gross_total_income: number;
  
  // Deductions
  section_80c: number;
  section_80d: number;
  section_80g: number;
  section_80e: number;
  section_80tta: number;
  total_deductions: number;
  
  // Tax calculation
  taxable_income: number;
  tax_before_relief: number;
  tax_relief: number;
  tax_payable: number;
  advance_tax_paid: number;
  tds_deducted: number;
  self_assessment_tax: number;
  refund_due: number;
  
  // Add missing properties that are being accessed
  details?: {
    regular_income: number;
    stcg_flat_rate: number;
    stcg_slab_rate: number;
    ltcg_112a: number;
    ltcg_other: number;
    dividend_income: number;
  };
  base_tax?: number;
  tax_after_rebate?: number;
  surcharge?: number;
  cess?: number;
}

// TaxationResponse and TaxationListResponse are now imported from ./taxation

// Form validation types
export interface ValidationError {
  field: string;
  message: string;
}

export interface FormErrors {
  [key: string]: string;
}

// Constants
export const TAX_REGIMES = {
  old: 'Old Regime',
  new: 'New Regime'
} as const;

export const FILING_STATUSES = {
  not_filed: 'Not Filed',
  filed: 'Filed',
  processed: 'Processed',
  verified: 'Verified',
  draft: 'Draft',
  submitted: 'Submitted',
  approved: 'Approved',
  rejected: 'Rejected',
  pending: 'Pending'
} as const;

export const USER_ROLES = {
  admin: 'Admin',
  hr: 'HR',
  employee: 'Employee',
  manager: 'Manager',
  superadmin: 'Super Admin'
} as const;

// Payroll Types
export interface PayrollData {
  employee_id: string;
  pay_period: string;
  gross_salary: number;
  net_salary: number;
  deductions: number;
  status: string;
}

// Attendance Types
export interface AttendanceData {
  employee_id: string;
  date: string;
  check_in: string;
  check_out: string;
  hours_worked: number;
  status: 'present' | 'absent' | 'late' | 'half_day';
}

// Leave Types
export interface LeaveData {
  employee_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days: number;
  status: 'pending' | 'approved' | 'rejected';
  reason: string;
}

// Organization Types
export interface OrganizationData {
  id: string;
  name: string;
  address: string;
  contact_email: string;
  contact_phone: string;
  industry: string;
  size: string;
}

// Reimbursement Types
export interface ReimbursementData {
  id: string;
  employee_id: string;
  type: string;
  amount: number;
  description: string;
  status: 'pending' | 'approved' | 'rejected';
  submitted_date: string;
  receipt_url?: string;
}

// Additional missing types
export interface AttendanceUserListSortConfig {
  key: string | 'lwp';
  direction: 'asc' | 'desc';
}

export interface LWPData {
  [employee_id: string]: number;
}

export interface LeaveBalanceData {
  [leave_type: string]: number;
}

export interface LeaveRequest {
  id?: string;
  _id?: string;
  employee_id: string;
  leave_type: string;
  leave_name?: string;
  leave_count?: number;
  start_date: string;
  end_date: string;
  days: number;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  applied_date: string;
  approved_by?: string;
  approved_date?: string;
  comments?: string;
}

export interface AlertState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

export interface ToastState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

export interface ReimbursementType {
  id?: string;
  type_id?: string;
  name?: string;
  category_name?: string;
  description?: string;
  max_amount?: number;
  max_limit?: number;
  requires_receipt?: boolean;
  is_receipt_required?: boolean;
  is_approval_required?: boolean;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

// Sort configuration for tables
export interface SortConfig {
  key: string | null;
  direction: 'asc' | 'desc';
}

// Dashboard statistics
export interface DashboardStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  checkin_count: number;
  checkout_count: number;
  pending_reimbursements: number;
  pending_reimbursements_amount: number;
  approved_reimbursements: number;
  approved_reimbursements_amount: number;
  pending_leaves: number;
  total_departments: number;
  recent_joiners_count: number;
  generated_at: string;
  department_distribution: Record<string, number>;
  role_distribution: Record<string, number>;
  attendance_trends: Record<string, any>;
  leave_trends: Record<string, any>;
  error_message?: string;
}

// Organisation interface
export interface Organisation {
  organisation_id: string;
  name: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  phone?: string;
  email?: string;
  website?: string;
  industry?: string;
  size?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

// Company Leave interface
export interface CompanyLeave {
  company_leave_id: string;
  leave_name: string;
  accrual_type: string;
  annual_allocation: number;
  encashable: boolean;
  is_allowed_on_probation: boolean;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

// Add missing taxation-related types
export interface SalaryComponents {
  basic: number;
  dearness_allowance: number;
  hra: number;
  hra_percentage?: number; // Additional property for compatibility
  actual_rent_paid?: number; // Additional property for compatibility
  special_allowance: number;
  bonus: number;
  commission?: number; // Add missing commission property
  city_compensatory_allowance?: number; // Add missing property
  rural_allowance?: number; // Add missing property
  proctorship_allowance: number;
  wardenship_allowance: number;
  project_allowance: number;
  deputation_allowance: number;
  interim_relief: number;
  tiffin_allowance: number;
  fixed_medical_allowance: number;
  overtime_allowance: number;
  servant_allowance: number;
  hills_high_altd_allowance: number;
  hills_high_altd_exemption_limit: number;
  border_remote_allowance: number;
  border_remote_exemption_limit: number;
  transport_employee_allowance: number;
  children_education_allowance: number;
  children_education_count: number;
  children_education_months: number;
  hostel_allowance: number;
  hostel_count: number;
  hostel_months: number;
  transport_allowance: number;
  transport_months: number;
  underground_mines_allowance: number;
  underground_mines_months: number;
  govt_employee_entertainment_allowance: number;
  govt_employees_outside_india_allowance: number;
  supreme_high_court_judges_allowance: number;
  judge_compensatory_allowance: number;
  section_10_14_special_allowances: number;
  travel_on_tour_allowance: number;
  tour_daily_charge_allowance: number;
  conveyance_in_performace_of_duties: number;
  helper_in_performace_of_duties: number;
  academic_research: number;
  uniform_allowance: number;
  any_other_allowance: number;
  any_other_allowance_exemption: number;
  hra_city: string;
  perquisites: Perquisites;
}

export interface OtherSources {
  interest_savings: number;
  interest_fd: number;
  interest_rd: number;
  post_office_interest: number;
  dividend_income: number;
  gifts: number;
  business_professional_income: number;
  other_income: number;
}

export interface CapitalGains {
  stcg_111a: number;
  stcg_any_other_asset: number;
  stcg_debt_mutual_fund: number;
  ltcg_112a: number;
  ltcg_any_other_asset: number;
  ltcg_debt_mutual_fund: number;
}

export interface LeaveEncashment {
  leave_encashment_income_received: number;
  leave_encashment_exemption: number;
  leave_encashment_taxable: number;
  leave_encashed?: number; // Additional property for compatibility
  is_deceased?: boolean; // Additional property for compatibility
  during_employment?: boolean; // Additional property for compatibility
}

export interface HouseProperty {
  property_type?: string; // Add missing property_type field
  annual_rent: number;
  municipal_taxes_paid: number;
  standard_deduction: number;
  interest_on_loan: number;
  net_income: number;
  property_address?: string; // Additional property for compatibility
  occupancy_status?: string; // Additional property for compatibility
  rent_income?: number; // Additional property for compatibility
  property_tax?: number; // Additional property for compatibility
  interest_on_home_loan?: number; // Additional property for compatibility
  pre_construction_loan_interest?: number; // Additional property for compatibility
}

export interface Pension {
  pension_received: number;
  commuted_pension: number;
  uncommuted_pension: number;
  total_pension_income?: number; // Additional property for compatibility
  computed_pension_percentage?: number; // Additional property for compatibility
  uncomputed_pension_frequency?: string; // Additional property for compatibility
  uncomputed_pension_amount?: number; // Additional property for compatibility
}

export interface VoluntaryRetirement {
  compensation_received: number;
  exemption_limit: number;
  taxable_amount: number;
  is_vrs_requested?: boolean; // Add missing property for compatibility
  voluntary_retirement_amount?: number; // Add missing property for compatibility
}

export interface Gratuity {
  gratuity_received: number;
  exemption_limit: number;
  taxable_amount: number;
  gratuity_income?: number; // Add missing property for compatibility
}

export interface RetrenchmentCompensation {
  compensation_received: number;
  exemption_limit: number;
  taxable_amount: number;
  retrenchment_amount?: number; // Add missing property for compatibility
  is_provided?: boolean; // Add missing property for compatibility
}

export interface Deductions {
  // Section 80C - Updated to match backend field names exactly
  section_80c: {
    life_insurance_premium: number;
    epf_contribution: number;
    ppf_contribution: number;
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
  
  // Section 80CCC - Updated to match backend field names exactly
  section_80ccc: {
    pension_fund_contribution: number;
  };
  
  // Section 80CCD - Updated to match backend field names exactly
  section_80ccd: {
    employee_nps_contribution: number;
    additional_nps_contribution: number;
    employer_nps_contribution: number;
  };
  
  // Section 80D - Updated to match backend field names exactly
  section_80d: {
    self_family_premium: number;
    parent_premium: number;
    preventive_health_checkup: number;
    employee_age: number;
    parent_age: number;
  };
  
  // Section 80DD - Updated to match backend field names exactly
  section_80dd: {
    relation: string;
    disability_percentage: string;
  };
  
  // Section 80DDB - Updated to match backend field names exactly
  section_80ddb: {
    dependent_age: number;
    medical_expenses: number;
    relation: string;
  };
  
  // Section 80E - Updated to match backend field names exactly
  section_80e: {
    education_loan_interest: number;
    relation: string;
  };
  
  // Section 80EEB - Updated to match backend field names exactly
  section_80eeb: {
    ev_loan_interest: number;
    ev_purchase_date: string;
  };
  
  // Section 80G - Updated to match backend field names exactly
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
  
  // Section 80GGC - Updated to match backend field names exactly
  section_80ggc: {
    political_party_contribution: number;
  };
  
  // Section 80U - Updated to match backend field names exactly
  section_80u: {
    disability_percentage: string;
  };
  
  // Section 80TTA/TTB - Updated to match backend field names exactly
  section_80tta_ttb: {
    savings_interest: number;
    fd_interest: number;
    rd_interest: number;
    post_office_interest: number;
    age: number;
  };
  
  // Legacy fields for backward compatibility (to be removed)
  section_24b?: number;
}

// Add missing dashboard and API response types
export interface TaxationDashboardData {
  // Properties for individual taxation records
  employee_id?: string;
  tax_year?: string;
  regime?: TaxRegime;
  filing_status?: FilingStatus;
  total_tax?: number;
  tax_paid?: number;
  tax_due?: number;
  tax_refundable?: number;
  
  // Tax breakup for detailed view
  tax_breakup?: ExtendedTaxBreakup;
  
  // Salary information
  salary?: SalaryComponents;
  
  // Other income sources
  other_sources?: OtherSources;
  capital_gains?: CapitalGains | number;
  
  // Deductions
  deductions?: Deductions;
  
  // Array format for list views
  records?: any[]; // Using any[] temporarily to avoid circular dependency
  total?: number;
  summary?: {
    total_tax: number;
    total_income: number;
    total_deductions: number;
  };
}

export interface FilingStatusOption {
  value: FilingStatus;
  label: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  message?: string;
}

export interface FileUploadOptions {
  maxSize: number;
  allowedTypes: string[];
  multiple: boolean;
} 