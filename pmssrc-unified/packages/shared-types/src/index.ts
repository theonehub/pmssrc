// Shared types for PMSSRC applications
// These types are based on the existing FastAPI backend structure

// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  organisation_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Attendance types
export interface AttendanceCreateRequest {
  check_in_time?: string;
  check_out_time?: string;
  location?: LocationData;
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'HALF_DAY';
}

export interface AttendanceRecord {
  id: string;
  user_id: string;
  check_in_time?: string;
  check_out_time?: string;
  location?: LocationData;
  status: 'PRESENT' | 'ABSENT' | 'LATE' | 'HALF_DAY';
  created_at: string;
  updated_at: string;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  accuracy?: number;
  timestamp?: number;
}

// Leave types
export interface LeaveRequest {
  user_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string;
  half_day?: boolean;
  half_day_type?: 'FIRST_HALF' | 'SECOND_HALF';
  attachments?: string[];
}

export interface LeaveRecord {
  id: string;
  user_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  approved_by?: string;
  approved_at?: string;
  half_day?: boolean;
  half_day_type?: 'FIRST_HALF' | 'SECOND_HALF';
  attachments?: string[];
  created_at: string;
  updated_at: string;
}

// Reimbursement types
export interface ReimbursementRequest {
  user_id: string;
  reimbursement_type: string;
  amount: number;
  description: string;
  date: string;
  category?: string;
  attachments?: string[];
}

export interface ReimbursementRecord {
  id: string;
  user_id: string;
  reimbursement_type: string;
  amount: number;
  description: string;
  date: string;
  category?: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  approved_by?: string;
  approved_at?: string;
  attachments?: string[];
  created_at: string;
  updated_at: string;
}

// Organisation types
export interface Organisation {
  id: string;
  name: string;
  address: string;
  contact_email: string;
  contact_phone: string;
  created_at: string;
  updated_at: string;
}

// Taxation types
export interface TaxCalculationRequest {
  user_id: string;
  financial_year: string;
  basic_salary: number;
  allowances: number;
  deductions: Deduction[];
  additional_income?: number;
  investments?: number;
}

export interface Deduction {
  type: string;
  amount: number;
  description?: string;
}

export interface TaxCalculationResponse {
  user_id: string;
  financial_year: string;
  gross_income: number;
  total_deductions: number;
  taxable_income: number;
  tax_liability: number;
  effective_tax_rate: number;
  old_regime_tax: number;
  new_regime_tax: number;
  recommended_regime: 'OLD' | 'NEW';
  potential_savings: number;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Common utility types
export type Status = 'ACTIVE' | 'INACTIVE' | 'PENDING' | 'APPROVED' | 'REJECTED';

export interface BaseEntity {
  id: string;
  created_at: string;
  updated_at: string;
}

// Leave and Reimbursement types
export type LeaveType = 'CASUAL' | 'SICK' | 'ANNUAL' | 'MATERNITY' | 'PATERNITY' | 'COMPENSATORY';
export type ReimbursementType = 'TRAVEL' | 'MEALS' | 'ACCOMMODATION' | 'EQUIPMENT' | 'TRAINING' | 'OTHER';
export type TaxRegime = 'OLD' | 'NEW'; 