import { get, post } from './baseApi';
import { DashboardStats } from '../types';

export interface UserAnalytics {
  total_users: number;
  active_users: number;
  inactive_users: number;
  department_distribution: Record<string, number>;
  role_distribution: Record<string, number>;
  recent_joiners: Array<{
    employee_id: string;
    name: string;
    department: string;
    date_of_joining: string;
  }>;
  user_growth_trends: Record<string, any>;
  generated_at: string;
}

export interface AttendanceAnalytics {
  total_checkins_today: number;
  total_checkouts_today: number;
  present_count: number;
  absent_count: number;
  late_arrivals: number;
  early_departures: number;
  average_working_hours: number;
  attendance_trends: Record<string, any>;
  department_attendance: Record<string, any>;
  generated_at: string;
}

export interface LeaveAnalytics {
  total_pending_leaves: number;
  total_approved_leaves: number;
  total_rejected_leaves: number;
  leave_type_distribution: Record<string, number>;
  department_leave_trends: Record<string, any>;
  monthly_leave_trends: Record<string, any>;
  generated_at: string;
}

export interface PayrollAnalytics {
  total_payouts_current_month: number;
  total_amount_current_month: number;
  average_salary: number;
  department_salary_distribution: Record<string, number>;
  salary_trends: Record<string, any>;
  
  // TDS Analytics
  total_tds_current_month: number;
  average_tds_per_employee: number;
  tds_trends: Record<string, any>;
  department_tds_distribution: Record<string, any>;
  
  generated_at: string;
}

export interface ReimbursementAnalytics {
  total_pending_reimbursements: number;
  total_pending_amount: number;
  total_approved_reimbursements: number;
  total_approved_amount: number;
  reimbursement_type_distribution: Record<string, any>;
  monthly_reimbursement_trends: Record<string, any>;
  generated_at: string;
}

export interface ConsolidatedAnalytics {
  dashboard_analytics: DashboardStats;
  user_analytics: UserAnalytics;
  attendance_analytics: AttendanceAnalytics;
  leave_analytics: LeaveAnalytics;
  payroll_analytics: PayrollAnalytics;
  reimbursement_analytics: ReimbursementAnalytics;
  generated_at: string;
}

export interface ExportRequest {
  report_type: string;
  format: 'pdf' | 'excel' | 'csv';
  start_date?: string;
  end_date?: string;
  filters?: Record<string, any>;
}

export interface ExportResponse {
  export_id: string;
  download_url: string;
  expires_at: string;
  file_size: number;
  format: string;
}

class ReportingService {
  /**
   * Get dashboard analytics - main overview statistics
   */
  async getDashboardAnalytics(): Promise<DashboardStats> {
    return await get<DashboardStats>('/api/v2/reporting/dashboard/analytics/statistics');
  }

  /**
   * Get consolidated analytics from all modules
   */
  async getConsolidatedAnalytics(startDate?: string, endDate?: string): Promise<ConsolidatedAnalytics> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    const url = `/api/v2/reporting/analytics/consolidated${queryString ? `?${queryString}` : ''}`;
    
    return await get<ConsolidatedAnalytics>(url);
  }

  /**
   * Get user analytics data
   */
  async getUserAnalytics(): Promise<UserAnalytics> {
    return await get<UserAnalytics>('/api/v2/reporting/analytics/users');
  }

  /**
   * Get attendance analytics data
   */
  async getAttendanceAnalytics(startDate?: string, endDate?: string): Promise<AttendanceAnalytics> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    const url = `/api/v2/reporting/analytics/attendance${queryString ? `?${queryString}` : ''}`;
    
    return await get<AttendanceAnalytics>(url);
  }

  /**
   * Get leave analytics data
   */
  async getLeaveAnalytics(startDate?: string, endDate?: string): Promise<LeaveAnalytics> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    const url = `/api/v2/reporting/analytics/leaves${queryString ? `?${queryString}` : ''}`;
    
    return await get<LeaveAnalytics>(url);
  }

  /**
   * Get payroll analytics data
   */
  async getPayrollAnalytics(startDate?: string, endDate?: string): Promise<PayrollAnalytics> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    const url = `/api/v2/reporting/analytics/payroll${queryString ? `?${queryString}` : ''}`;
    
    return await get<PayrollAnalytics>(url);
  }

  /**
   * Get reimbursement analytics data
   */
  async getReimbursementAnalytics(startDate?: string, endDate?: string): Promise<ReimbursementAnalytics> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    const url = `/api/v2/reporting/analytics/reimbursements${queryString ? `?${queryString}` : ''}`;
    
    return await get<ReimbursementAnalytics>(url);
  }

  /**
   * Export report data
   */
  async exportReport(request: ExportRequest): Promise<ExportResponse> {
    return await post<ExportResponse>('/api/v2/reporting/export', request);
  }

  /**
   * Download exported report
   */
  downloadExportedReport(downloadUrl: string, filename: string): void {
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  /**
   * Get module health status
   */
  async getHealthStatus(): Promise<{ status: string; module: string; version: string; features: string[] }> {
    return await get('/api/v2/reporting/health');
  }
}

const reportingService = new ReportingService();
export default reportingService; 