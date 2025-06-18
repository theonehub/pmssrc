import { BaseAPI } from '../api/baseApi';

// Monthly Payout Types
export interface MonthlyPayoutRequest {
  employee_id: string;
  month: number;
  year: number;
  lwp_days?: number;
  total_working_days?: number;
  advance_deduction?: number;
  loan_deduction?: number;
  other_deductions?: number;
  auto_approve?: boolean;
}

export interface BulkPayoutRequest {
  month: number;
  year: number;
  employee_ids: string[];
  employee_lwp_details: Record<string, {
    lwp_days?: number;
    total_working_days?: number;
    advance_deduction?: number;
    loan_deduction?: number;
    other_deductions?: number;
  }>;
  auto_approve?: boolean;
}

export interface MonthlyPayoutResponse {
  id: string;
  employee_id: string;
  employee_name: string;
  month: number;
  year: number;
  status: string;
  
  // Salary components
  base_monthly_gross: number;
  adjusted_monthly_gross: number;
  monthly_net_salary: number;
  total_monthly_deductions: number;
  
  // LWP details
  lwp_days: number;
  lwp_factor: number;
  lwp_deduction_amount: number;
  
  // Deductions breakdown
  epf_employee_amount: number;
  esi_employee_amount: number;
  professional_tax_amount: number;
  monthly_tds_amount: number;
  advance_deduction: number;
  loan_deduction: number;
  other_deductions: number;
  
  // Workflow
  calculation_date: string;
  approved_by?: string;
  approved_date?: string;
  processed_by?: string;
  processed_date?: string;
  payment_reference?: string;
  payment_date?: string;
  remarks?: string;
}

export interface PayoutSearchFilters {
  employee_id?: string;
  month?: number;
  year?: number;
  status?: string;
  department?: string;
  page?: number;
  size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PayoutSummary {
  total_employees: number;
  total_gross_amount: number;
  total_net_amount: number;
  total_lwp_deduction: number;
  status_breakdown: Record<string, number>;
  department_breakdown: Record<string, {
    employee_count: number;
    total_amount: number;
  }>;
}

export interface LWPAnalytics {
  total_employees_with_lwp: number;
  total_lwp_days: number;
  total_lwp_deduction: number;
  average_lwp_days: number;
  department_wise_lwp: Record<string, {
    employee_count: number;
    total_lwp_days: number;
    total_deduction: number;
  }>;
}

class MonthlyPayoutService {
  private baseApi: BaseAPI;

  constructor() {
    this.baseApi = BaseAPI.getInstance();
  }

  /**
   * Compute monthly payout for a single employee
   */
  async computeEmployeePayout(request: MonthlyPayoutRequest): Promise<MonthlyPayoutResponse> {
    try {
      const response = await this.baseApi.post('/api/v2/monthly-payouts/compute', request);
      return response.data;
    } catch (error) {
      console.error('Error computing employee payout:', error);
      throw error;
    }
  }

  /**
   * Compute monthly payouts for multiple employees
   */
  async computeBulkPayouts(request: BulkPayoutRequest): Promise<{
    successful_payouts: MonthlyPayoutResponse[];
    failed_payouts: Array<{ employee_id: string; error: string }>;
    summary: {
      total_employees: number;
      successful_count: number;
      failed_count: number;
      total_gross_amount: number;
      total_net_amount: number;
      total_lwp_deduction: number;
    };
  }> {
    try {
      const response = await this.baseApi.post('/api/v2/monthly-payouts/bulk-compute', request);
      return response.data;
    } catch (error) {
      console.error('Error computing bulk payouts:', error);
      throw error;
    }
  }

  /**
   * Search monthly payouts with filters
   */
  async searchPayouts(filters: PayoutSearchFilters = {}): Promise<{
    payouts: MonthlyPayoutResponse[];
    total_count: number;
    page: number;
    size: number;
    total_pages: number;
  }> {
    try {
      const response = await this.baseApi.get('/api/v2/monthly-payouts/search', { params: filters });
      return response.data;
    } catch (error) {
      console.error('Error searching payouts:', error);
      throw error;
    }
  }

  /**
   * Get monthly payout by employee ID, month, and year
   */
  async getEmployeePayout(employeeId: string, month: number, year: number): Promise<MonthlyPayoutResponse | null> {
    try {
      const response = await this.baseApi.get(`/api/v2/monthly-payouts/${employeeId}/${month}/${year}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      console.error('Error getting employee payout:', error);
      throw error;
    }
  }

  /**
   * Update monthly payout
   */
  async updatePayout(employeeId: string, month: number, year: number, updates: {
    advance_deduction?: number;
    loan_deduction?: number;
    other_deductions?: number;
    remarks?: string;
  }): Promise<MonthlyPayoutResponse> {
    try {
      const response = await this.baseApi.put(`/api/v2/monthly-payouts/${employeeId}/${month}/${year}`, updates);
      return response.data;
    } catch (error) {
      console.error('Error updating payout:', error);
      throw error;
    }
  }

  /**
   * Approve monthly payout
   */
  async approvePayout(employeeId: string, month: number, year: number, remarks?: string): Promise<MonthlyPayoutResponse> {
    try {
      const response = await this.baseApi.put(`/api/v2/monthly-payouts/${employeeId}/${month}/${year}/approve`, {
        remarks
      });
      return response.data;
    } catch (error) {
      console.error('Error approving payout:', error);
      throw error;
    }
  }

  /**
   * Process monthly payout
   */
  async processPayout(employeeId: string, month: number, year: number, paymentReference?: string): Promise<MonthlyPayoutResponse> {
    try {
      const response = await this.baseApi.put(`/api/v2/monthly-payouts/${employeeId}/${month}/${year}/process`, {
        payment_reference: paymentReference
      });
      return response.data;
    } catch (error) {
      console.error('Error processing payout:', error);
      throw error;
    }
  }

  /**
   * Get monthly payout summary
   */
  async getPayoutSummary(month: number, year: number): Promise<PayoutSummary> {
    try {
      const response = await this.baseApi.get(`/api/v2/monthly-payouts/summary/${month}/${year}`);
      return response.data;
    } catch (error) {
      console.error('Error getting payout summary:', error);
      throw error;
    }
  }

  /**
   * Generate payslip for an employee
   */
  async generatePayslip(employeeId: string, month: number, year: number): Promise<any> {
    try {
      const response = await this.baseApi.get(`/api/v2/monthly-payouts/${employeeId}/${month}/${year}/payslip`);
      return response.data;
    } catch (error) {
      console.error('Error generating payslip:', error);
      throw error;
    }
  }

  /**
   * Download payslip PDF
   */
  async downloadPayslip(employeeId: string, month: number, year: number): Promise<void> {
    try {
      const response = await this.baseApi.get(`/api/v2/monthly-payouts/${employeeId}/${month}/${year}/payslip/download`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `payslip-${employeeId}-${month}-${year}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading payslip:', error);
      throw error;
    }
  }

  /**
   * Get employee history
   */
  async getEmployeeHistory(employeeId: string, limit: number = 12): Promise<MonthlyPayoutResponse[]> {
    try {
      const response = await this.baseApi.get(`/api/v2/monthly-payouts/employee/${employeeId}/history`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error getting employee history:', error);
      throw error;
    }
  }

  /**
   * Get LWP analytics
   */
  async getLWPAnalytics(month: number, year: number): Promise<LWPAnalytics> {
    try {
      const response = await this.baseApi.get(`/api/v2/monthly-payouts/analytics/lwp-impact/${month}/${year}`);
      return response.data;
    } catch (error) {
      console.error('Error getting LWP analytics:', error);
      throw error;
    }
  }

  /**
   * Get department summary
   */
  async getDepartmentSummary(month: number, year: number): Promise<Record<string, {
    employee_count: number;
    total_gross: number;
    total_net: number;
    total_lwp_deduction: number;
    average_salary: number;
  }>> {
    try {
      const response = await this.baseApi.get(`/api/v2/monthly-payouts/analytics/department-summary/${month}/${year}`);
      return response.data;
    } catch (error) {
      console.error('Error getting department summary:', error);
      throw error;
    }
  }

  /**
   * Bulk approve payouts
   */
  async bulkApprove(month: number, year: number, employeeIds: string[], remarks?: string): Promise<{
    successful: string[];
    failed: Array<{ employee_id: string; error: string }>;
  }> {
    try {
      const response = await this.baseApi.post('/api/v2/monthly-payouts/bulk-approve', {
        month,
        year,
        employee_ids: employeeIds,
        remarks
      });
      return response.data;
    } catch (error) {
      console.error('Error bulk approving payouts:', error);
      throw error;
    }
  }

  /**
   * Bulk process payouts
   */
  async bulkProcess(month: number, year: number, employeeIds: string[], paymentReference?: string): Promise<{
    successful: string[];
    failed: Array<{ employee_id: string; error: string }>;
  }> {
    try {
      const response = await this.baseApi.post('/api/v2/monthly-payouts/bulk-process', {
        month,
        year,
        employee_ids: employeeIds,
        payment_reference: paymentReference
      });
      return response.data;
    } catch (error) {
      console.error('Error bulk processing payouts:', error);
      throw error;
    }
  }

  // Utility methods
  getCurrentFinancialYear(): number {
    const today = new Date();
    const currentMonth = today.getMonth() + 1;
    const currentYear = today.getFullYear();
    return currentMonth >= 4 ? currentYear : currentYear - 1;
  }

  getFinancialYearLabel(year: number): string {
    return `${year}-${year + 1}`;
  }

  getMonthName(month: number): string {
    return new Date(0, month - 1).toLocaleString('default', { month: 'long' });
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  getStatusColor(status: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' {
    switch (status.toLowerCase()) {
      case 'paid':
        return 'success';
      case 'processed':
        return 'info';
      case 'approved':
        return 'primary';
      case 'calculated':
        return 'secondary';
      case 'failed':
      case 'cancelled':
        return 'error';
      case 'pending_approval':
        return 'warning';
      default:
        return 'default';
    }
  }

  getStatusLabel(status: string): string {
    switch (status.toLowerCase()) {
      case 'pending_approval':
        return 'Pending Approval';
      case 'calculated':
        return 'Calculated';
      case 'approved':
        return 'Approved';
      case 'processed':
        return 'Processed';
      case 'paid':
        return 'Paid';
      case 'failed':
        return 'Failed';
      case 'cancelled':
        return 'Cancelled';
      case 'draft':
        return 'Draft';
      default:
        return status;
    }
  }
}

export default new MonthlyPayoutService(); 