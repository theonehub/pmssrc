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
  profile_picture?: string; // Profile picture URL/path
}

export type UserRole = 'admin' | 'hr' | 'employee' | 'manager' | 'superadmin' | 'user';

// Import taxation types from dedicated file
export * from './taxation';

export type TaxRegime = 'old' | 'new';
export type FilingStatus = 'not_filed' | 'filed' | 'processed' | 'verified' | 'draft' | 'submitted' | 'approved' | 'rejected' | 'pending';

export interface AlertState {
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

export interface LeaveRequest {
  id?: string;
  _id?: string;
  leave_id?: string;
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

export interface LeaveBalanceData {
  [leave_type: string]: number;
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

export interface AttendanceUserListSortConfig {
  key: string | 'lwp';
  direction: 'asc' | 'desc';
}

export interface LWPData {
  [employee_id: string]: number;
}

export interface SortConfig {
  key: string | null;
  direction: 'asc' | 'desc';
} 