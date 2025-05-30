// User Types
export interface User {
  emp_id: string;
  name: string;
  email: string;
  gender: 'Male' | 'Female' | 'Other';
  dob: string;
  doj: string;
  mobile: string;
  manager_id?: string;
  role: UserRole;
  pan_number?: string;
  uan_number?: string;
  aadhar_number?: string;
  department?: string;
  designation?: string;
  location?: string;
  esi_number?: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export type UserRole = 'user' | 'manager' | 'hr' | 'admin' | 'superadmin';

// Authentication Types
export interface LoginCredentials {
  username: string;
  password: string;
  hostname?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token?: string;
  user_info: {
    emp_id: string;
    name: string;
    email: string;
    role: UserRole;
    department: string;
    position: string;
  };
  permissions: string[];
  last_login?: string;
  login_time: string;
}

export interface TokenData {
  emp_id: string;
  role: UserRole;
  exp: number;
  iat: number;
  sub?: string; // JWT subject claim (alternative to emp_id)
}

// Attendance Types
export interface AttendanceRecord {
  id?: string;
  emp_id: string;
  date: string;
  check_in?: string;
  check_out?: string;
  status: AttendanceStatus;
  total_hours?: number;
  break_hours?: number;
  overtime_hours?: number;
  created_at?: string;
  updated_at?: string;
}

export type AttendanceStatus =
  | 'present'
  | 'absent'
  | 'half_day'
  | 'late'
  | 'early_departure';

// Leave Types
export interface LeaveApplication {
  leave_id?: string;
  emp_id: string;
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  status: LeaveStatus;
  applied_date?: string;
  approved_by?: string;
  approved_date?: string;
  comments?: string;
}

export type LeaveType =
  | 'casual_leave'
  | 'sick_leave'
  | 'earned_leave'
  | 'maternity_leave'
  | 'paternity_leave';
export type LeaveStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';

export interface LeaveBalance {
  emp_id: string;
  casual_leave: number;
  sick_leave: number;
  earned_leave: number;
  maternity_leave?: number;
  paternity_leave?: number;
  total_available: number;
  total_used: number;
}

// Reimbursement Types
export interface ReimbursementRequest {
  id?: string;
  emp_id: string;
  type: string;
  amount: number;
  description: string;
  receipt_url?: string;
  status: ReimbursementStatus;
  submitted_date?: string;
  approved_by?: string;
  approved_date?: string;
  comments?: string;
}

export type ReimbursementStatus = 'pending' | 'approved' | 'rejected' | 'paid';

// MyReimbursements Component Types
export interface MyReimbursementRequest {
  id: string;
  reimbursement_type_id: string;
  amount: number;
  note?: string;
  status: ReimbursementStatus;
  created_at: string;
  file_path?: string;
}

export interface ReimbursementType {
  id: string;
  name: string;
  max_limit?: number;
  description?: string;
  is_active?: boolean;
}

export interface ReimbursementFormData {
  reimbursement_type_id: string;
  amount: string;
  note: string;
  file: File | null;
}

export interface ToastState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

// Taxation Types
export interface TaxationData {
  emp_id: string;
  tax_year: string;
  regime: TaxRegime;
  filing_status: FilingStatus;
  emp_age?: number;
  is_govt_employee: boolean;
  salary: SalaryComponents;
  other_sources: OtherSources;
  capital_gains: CapitalGains;
  house_property: HouseProperty;
  deductions: Deductions;
  leave_encashment?: LeaveEncashment;
  pension?: Pension;
  gratuity?: Gratuity;
  voluntary_retirement?: VoluntaryRetirement;
  retrenchment_compensation?: RetrenchmentCompensation;
  tax_breakup?: TaxBreakup;
  tax_payable: number;
  tax_paid: number;
  tax_due: number;
  tax_refundable: number;
  tax_pending: number;
  created_at?: string;
  updated_at?: string;
}

export type TaxRegime = 'old' | 'new';
export type FilingStatus = 'draft' | 'submitted' | 'filed' | 'processed';

export interface SalaryComponents {
  basic: number;
  dearness_allowance: number;
  hra_city: string;
  hra_percentage: number;
  hra: number;
  actual_rent_paid: number;
  special_allowance: number;
  bonus: number;
  commission: number;
  city_compensatory_allowance: number;
  rural_allowance: number;
  proctorship_allowance: number;
  wardenship_allowance: number;
  project_allowance: number;
  deputation_allowance: number;
  overtime_allowance: number;
  interim_relief: number;
  tiffin_allowance: number;
  fixed_medical_allowance: number;
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
  any_other_allowance: number;
  any_other_allowance_exemption: number;
  travel_on_tour_allowance: number;
  tour_daily_charge_allowance: number;
  conveyance_in_performace_of_duties: number;
  helper_in_performace_of_duties: number;
  academic_research: number;
  uniform_allowance: number;
  perquisites: Perquisites;
}

export interface Perquisites {
  // Accommodation perquisites
  accommodation_provided: string;
  accommodation_govt_lic_fees: number;
  accommodation_city_population: string;
  accommodation_rent: number;
  is_furniture_owned: boolean;
  furniture_actual_cost: number;
  furniture_cost_to_employer: number;
  furniture_cost_paid_by_employee: number;

  // Car perquisites
  is_car_rating_higher: boolean;
  is_car_employer_owned: boolean;
  is_expenses_reimbursed: boolean;
  is_driver_provided: boolean;
  car_use: string;
  car_cost_to_employer: number;
  month_counts: number;
  other_vehicle_cost_to_employer: number;
  other_vehicle_month_counts: number;

  // Medical Reimbursement
  is_treated_in_India: boolean;
  medical_reimbursement_by_employer: number;
  travelling_allowance_for_treatment: number;
  rbi_limit_for_illness: number;

  // Leave Travel Allowance
  lta_amount_claimed: number;
  lta_claimed_count: number;
  travel_through: string;
  public_transport_travel_amount_for_same_distance: number;
  lta_claim_start_date: string;
  lta_claim_end_date: string;

  // Free Education
  employer_maintained_1st_child: boolean;
  monthly_count_1st_child: number;
  employer_monthly_expenses_1st_child: number;
  employer_maintained_2nd_child: boolean;
  monthly_count_2nd_child: number;
  employer_monthly_expenses_2nd_child: number;

  // Gas, Electricity, Water
  is_gas_manufactured_by_employer: boolean;
  gas_amount_paid_by_employer: number;
  gas_amount_paid_by_employee: number;
  is_electricity_manufactured_by_employer: boolean;
  electricity_amount_paid_by_employer: number;
  electricity_amount_paid_by_employee: number;
  is_water_manufactured_by_employer: boolean;
  water_amount_paid_by_employer: number;
  water_amount_paid_by_employee: number;

  // Domestic help
  domestic_help_amount_paid_by_employer: number;
  domestic_help_amount_paid_by_employee: number;

  // Interest-free/concessional loan
  loan_type: string;
  loan_amount: number;
  loan_interest_rate_company: number;
  loan_interest_rate_sbi: number;
  loan_month_count: number;
  loan_start_date: string;
  loan_end_date: string;

  // Lunch/Refreshment
  lunch_amount_paid_by_employer: number;
  lunch_amount_paid_by_employee: number;

  // ESOP & Stock Options fields
  number_of_esop_shares_exercised: number;
  esop_exercise_price_per_share: number;
  esop_allotment_price_per_share: number;
  grant_date: string | null;
  vesting_date: string | null;
  exercise_date: string | null;
  vesting_period: number;
  exercise_period: number;
  exercise_price_per_share: number;

  // Movable Asset
  mau_ownership: string;
  mau_value_to_employer: number;
  mau_value_to_employee: number;
  mat_type: string;
  mat_value_to_employer: number;
  mat_value_to_employee: number;
  mat_number_of_completed_years_of_use: number;

  // Monetary Benefits
  monetary_amount_paid_by_employer: number;
  expenditure_for_offical_purpose: number;
  monetary_benefits_amount_paid_by_employee: number;
  gift_vouchers_amount_paid_by_employer: number;

  // Club Expenses
  club_expenses_amount_paid_by_employer: number;
  club_expenses_amount_paid_by_employee: number;
  club_expenses_amount_paid_for_offical_purpose: number;
}

export interface OtherSources {
  interest_savings: number;
  interest_fd: number;
  interest_rd: number;
  dividend_income: number;
  gifts: number;
  other_interest: number;
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

export interface HouseProperty {
  property_address: string;
  occupancy_status: string;
  rent_income: number;
  property_tax: number;
  interest_on_home_loan: number;
  pre_construction_loan_interest: number;
}

export interface Deductions {
  section_80c_lic: number;
  section_80c_epf: number;
  section_80c_ssp: number;
  section_80c_nsc: number;
  section_80c_ulip: number;
  section_80c_tsmf: number;
  section_80c_tffte2c: number;
  section_80c_paphl: number;
  section_80c_sdpphp: number;
  section_80c_tsfdsb: number;
  section_80c_scss: number;
  section_80c_others: number;
  section_80ccc_ppic: number;
  section_80ccd_1_nps: number;
  section_80ccd_1b_additional: number;
  section_80ccd_2_enps: number;
  section_80d_hisf: number;
  section_80d_phcs: number;
  section_80d_hi_parent: number;
  section_80dd: number;
  relation_80dd: string;
  disability_percentage: string;
  section_80ddb: number;
  relation_80ddb: string;
  age_80ddb: number;
  section_80e_interest: number;
  relation_80e: string;
  section_80eeb: number;
  ev_purchase_date: string | null;
  section_80g_100_wo_ql: number;
  section_80g_100_head: string;
  section_80g_50_wo_ql: number;
  section_80g_50_head: string;
  section_80g_100_ql: number;
  section_80g_100_ql_head: string;
  section_80g_50_ql: number;
  section_80g_50_ql_head: string;
  section_80ggc: number;
  section_80u: number;
  disability_percentage_80u: string;
}

export interface TaxBreakup {
  gross_total_income: number;
  total_deductions: number;
  taxable_income: number;
  tax_before_relief: number;
  tax_relief: number;
  tax_payable: number;
  details?: Record<string, number>;
}

export interface LeaveEncashment {
  leave_encashment_income_received: number;
  leave_encashed: number;
  is_deceased: boolean;
  during_employment: boolean;
}

export interface Pension {
  total_pension_income: number;
  computed_pension_percentage: number;
  uncomputed_pension_frequency: string;
  uncomputed_pension_amount: number;
}

export interface Gratuity {
  gratuity_income: number;
}

export interface VoluntaryRetirement {
  is_vrs_requested: boolean;
  voluntary_retirement_amount: number;
}

export interface RetrenchmentCompensation {
  is_provided: boolean;
  retrenchment_amount: number;
}

// Payroll Types
export interface PayrollData {
  emp_id: string;
  month: string;
  year: number;
  basic_salary: number;
  allowances: Record<string, number>;
  deductions: Record<string, number>;
  gross_salary: number;
  net_salary: number;
  tax_deducted: number;
  pf_deduction: number;
  esi_deduction: number;
  status: PayrollStatus;
  generated_date?: string;
  paid_date?: string;
}

export type PayrollStatus = 'draft' | 'processed' | 'paid' | 'cancelled';

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
  errors?: Record<string, string>;
}

export interface PaginatedResponse<T = any> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

// Form Types
export interface ValidationResult {
  isValid: boolean;
  message: string;
}

export interface FormErrors {
  [key: string]: string;
}

// File Upload Types
export interface FileUploadOptions {
  maxSize?: number;
  allowedTypes?: string[];
  required?: boolean;
}

export interface UploadedFile {
  name: string;
  size: number;
  type: string;
  url?: string;
}

// Component Props Types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface LoadingProps {
  loading?: boolean;
  message?: string;
}

export interface ErrorProps {
  error?: string | null;
  onRetry?: () => void;
}

// Navigation Types
export interface RouteConfig {
  path: string;
  component: React.ComponentType;
  exact?: boolean;
  roles?: UserRole[];
}

// Theme Types
export interface ThemeConfig {
  mode: 'light' | 'dark';
  primaryColor: string;
  secondaryColor: string;
}

// Notification Types
export interface NotificationData {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
  read: boolean;
  action?: {
    label: string;
    url: string;
  };
}

// Dashboard Types
export interface DashboardStats {
  total_users: number;
  checkin_count: number;
  checkout_count: number;
  hr: number;
  lead: number;
  user: number;
  pending_leaves: number;
  pending_reimbursements: number;
}

// UsersList Component Types
export interface UsersListResponse {
  users: User[];
  total: number;
}

export interface SortConfig {
  key: keyof User | null;
  direction: 'asc' | 'desc';
}

export interface AlertState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

// AttendanceUserList Component Types
export interface LWPData {
  [empId: string]: number;
}

export interface AttendanceUserListSortConfig {
  key: keyof User | 'lwp' | null;
  direction: 'asc' | 'desc';
}

// LeaveManagement Component Types
export interface LeaveRequest {
  id?: string;
  leave_id?: string;
  _id?: string;
  leave_name: string;
  start_date: string;
  end_date: string;
  leave_count?: number;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
}

export interface LeaveBalanceData {
  [leaveType: string]: number;
}

// TaxationDashboard Component Types
export interface TaxYearOption {
  value: string;
  label: string;
}

export interface FilingStatusOption {
  value: string;
  label: string;
}

export interface TaxationDashboardData extends TaxationData {
  total_tax: number;
  tax_paid: number;
  tax_due: number;
  tax_refundable: number;
  tax_pending: number;
}

export interface TaxBreakupDetails {
  regular_income?: number;
  stcg_flat_rate?: number;
  stcg_slab_rate?: number;
  ltcg_112a?: number;
  ltcg_other?: number;
  dividend_income?: number;
  base_tax?: number;
  tax_after_rebate?: number;
  surcharge?: number;
  cess?: number;
  [key: string]: number | undefined; // Index signature for compatibility
}

export interface ExtendedTaxBreakup extends Omit<TaxBreakup, 'details'> {
  details?: TaxBreakupDetails;
  base_tax?: number;
  tax_after_rebate?: number;
  surcharge?: number;
  cess?: number;
}

// Organization Types
export interface Organization {
  id: string;
  name: string;
  hostname: string;
  email?: string;
  phone?: string;
  address?: string;
  pan_number?: string;
  gst_number?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
