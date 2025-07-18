import apiClient from '../utils/apiClient';

export interface PayoutStatusDTO {
  status: string;
  comments?: string | null;
  transaction_id?: string | null;
  transfer_date?: string | null; // ISO date string
}

export interface TDSStatus {
  status: string;
  challan_number?: string | null;
  month: number;
  total_tax_liability: number;
  paid: boolean;
}

export interface PfStatus {
  status: string;
  comments?: string | null;
  transaction_id?: string | null;
  transfer_date?: string | null;
}

export interface MonthlySalaryResponse {
  employee_id: string;
  month: number;
  year: number;
  tax_year: string;
  employee_name: string | null;
  employee_email: string | null;
  department: string | null;
  designation: string | null;
  basic_salary: number;
  da: number;
  hra: number;
  special_allowance: number;
  transport_allowance: number;
  medical_allowance: number;
  commission: number;
  other_allowances: number;
  one_time_arrear: number;
  one_time_bonus: number;
  epf_employee: number;
  epf_employer: number;
  eps_employee: number;
  eps_employer: number;
  vps_employee: number;
  esi_contribution: number;
  esi_employee: number;
  tds: number;
  advance_deduction: number;
  loan_deduction: number;
  other_deductions: number;
  gross_salary: number;
  total_deductions: number;
  net_salary: number;
  annual_gross_salary: number;
  annual_tax_liability: number;
  tax_regime: string;
  tax_exemptions: number;
  standard_deduction: number;
  total_days_in_month: number;
  working_days_in_period: number;
  lwp_days: number;
  effective_working_days: number;
  payout_status?: PayoutStatusDTO; // New field for payout status
  tds_status?: TDSStatus; // <-- Added this line
  pf_status?: PfStatus;
  computation_date: string | null;
  notes: string | null;
  remarks: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
  use_declared_values?: boolean;
  computation_mode?: string;
  computation_summary?: any;
}

export interface MonthlySalaryListResponse {
  items: MonthlySalaryResponse[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface MonthlySalarySummaryResponse {
  month: number;
  year: number;
  tax_year: string;
  total_employees: number;
  computed_count: number;
  pending_count: number;
  approved_count: number;
  paid_count: number;
  total_gross_payroll: number;
  total_net_payroll: number;
  total_deductions: number;
  total_tds: number;
  computation_completion_rate: number;
  last_computed_at: string | null;
  next_processing_date: string | null;
}

export interface MonthlySalaryComputeRequest {
  employee_id: string;
  month: number;
  year: number;
  tax_year: string;
  one_time_arrear?: number;
  one_time_bonus?: number;
  use_declared_values?: boolean;
  force_recompute?: boolean;
  computed_by?: string;
}

export interface MonthlySalaryBulkComputeRequest {
  month: number;
  year: number;
  tax_year: string;
  employee_ids?: string[];
  force_recompute?: boolean;
  computed_by?: string;
}

export interface MonthlySalaryBulkComputeResponse {
  total_requested: number;
  successful: number;
  failed: number;
  skipped: number;
  errors: Array<{
    employee_id: string;
    error: string;
  }>;
  computation_summary: any;
}

export interface MonthlySalaryStatusUpdateRequest {
  employee_id: string;
  month: number;
  year: number;
  tax_year: string; // Add this field to match backend and frontend usage
  comments: string;
  payout_status?: string;
  transaction_id?: string | undefined;
  transfer_date?: string | undefined; // ISO date string
  updated_by?: string;
  // Add these fields for TDS status update
  tds_status?: string;
  challan_number?: string | undefined;
}

export interface MonthlySalaryPaymentRequest {
  employee_id: string;
  month: number;
  year: number;
  payment_type: 'salary' | 'tds' | 'both';
  payment_reference?: string;
  payment_notes?: string;
  paid_by?: string;
}

export const salaryProcessingApi = {
  /**
   * Get monthly salaries for a period
   */
  async getMonthlySalariesForPeriod(
    month: number,
    taxYear: string,
    params?: {
      status?: string;
      department?: string;
      skip?: number;
      limit?: number;
    }
  ): Promise<MonthlySalaryListResponse> {
    const queryParams = new URLSearchParams();
    
    if (params?.status) queryParams.append('status', params.status);
    if (params?.department) queryParams.append('department', params.department);
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());

    const url = `/api/v2/taxation/monthly-salary/period/month/${month}/tax-year/${taxYear}`;
    const fullUrl = queryParams.toString() ? `${url}?${queryParams.toString()}` : url;

    const response = await apiClient.get(fullUrl);
    return response.data;
  },

  /**
   * Compute monthly salary for an employee
   */
  async computeMonthlySalary(
    request: MonthlySalaryComputeRequest
  ): Promise<MonthlySalaryResponse> {
    const response = await apiClient.post('/api/v2/taxation/monthly-salary/compute', request);
    return response.data;
  },

  /**
   * Get monthly salary summary for a period
   */
  async getMonthlySalarySummary(
    month: number,
    taxYear: string
  ): Promise<MonthlySalarySummaryResponse> {
    const response = await apiClient.get(
      `/api/v2/taxation/monthly-salary/summary/month/${month}/tax-year/${taxYear}`
    );
    return response.data;
  },

  /**
   * Delete monthly salary record
   */
  async deleteMonthlySalary(
    employeeId: string,
    month: number,
    taxYear: string
  ): Promise<{ message: string }> {
    const response = await apiClient.delete(
      `/api/v2/taxation/monthly-salary/employee/${employeeId}/month/${month}/tax-year/${taxYear}`
    );
    return response.data;
  },

  /**
   * Get salary history for a specific employee
   */
  async getEmployeeSalaryHistory(
    employeeId: string,
    limit: number = 100,
    offset: number = 0
  ): Promise<MonthlySalaryResponse[]> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (offset) params.append('offset', offset.toString());
    const url = `/api/v2/taxation/monthly-salary/employee/${employeeId}/history?${params.toString()}`;
    const response = await apiClient.get(url);
    return response.data;
  },

  /**
   * Download payslip for a specific month
   */
  async downloadPayslip(
    employeeId: string,
    month: number,
    year: number
  ): Promise<Blob> {
    const url = `/api/v2/taxation/monthly-salary/employee/${employeeId}/month/${month}/year/${year}/payslip`;
    const response = await apiClient.get(url, {
      responseType: 'blob'
    });
    return response.data;
  },

  /**
   * Update monthly salary status (with comments, transaction ID, transfer date)
   */
  async updateMonthlySalaryStatus(
    request: MonthlySalaryStatusUpdateRequest
  ): Promise<MonthlySalaryResponse> {
    const response = await apiClient.put('/api/v2/taxation/monthly-salary/status', request);
    return response.data;
  }
}; 