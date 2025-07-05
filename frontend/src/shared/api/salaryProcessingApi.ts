import apiClient from '../utils/apiClient';

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
  bonus: number;
  commission: number;
  other_allowances: number;
  epf_employee: number;
  esi_employee: number;
  professional_tax: number;
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
  status: string;
  computation_date: string | null;
  notes: string | null;
  remarks: string | null;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
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
  arrears?: number;
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
  status: string;
  notes?: string;
  updated_by?: string;
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
   * Get monthly salary for a specific employee
   */
  async getMonthlySalary(
    employeeId: string,
    month: number,
    year: number
  ): Promise<MonthlySalaryResponse> {
    const response = await apiClient.get(
      `/api/v2/monthly-salary/employee/${employeeId}/month/${month}/year/${year}`
    );
    return response.data;
  },

  /**
   * Get monthly salaries for a period
   */
  async getMonthlySalariesForPeriod(
    month: number,
    year: number,
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

    const url = `/api/v2/monthly-salary/period/month/${month}/year/${year}`;
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
   * Bulk compute monthly salaries
   */
  async bulkComputeMonthlySalaries(
    request: MonthlySalaryBulkComputeRequest
  ): Promise<MonthlySalaryBulkComputeResponse> {
    const response = await apiClient.post('/api/v2/monthly-salary/bulk-compute', request);
    return response.data;
  },

  /**
   * Update monthly salary status
   */
  async updateMonthlySalaryStatus(
    request: MonthlySalaryStatusUpdateRequest
  ): Promise<MonthlySalaryResponse> {
    const response = await apiClient.put('/api/v2/monthly-salary/status', request);
    return response.data;
  },

  /**
   * Get monthly salary summary for a period
   */
  async getMonthlySalarySummary(
    month: number,
    year: number
  ): Promise<MonthlySalarySummaryResponse> {
    const response = await apiClient.get(
      `/api/v2/monthly-salary/summary/month/${month}/year/${year}`
    );
    return response.data;
  },

  /**
   * Mark salary payment
   */
  async markSalaryPayment(
    request: MonthlySalaryPaymentRequest
  ): Promise<MonthlySalaryResponse> {
    const response = await apiClient.put('/api/v2/monthly-salary/payment', request);
    return response.data;
  },

  /**
   * Delete monthly salary record
   */
  async deleteMonthlySalary(
    employeeId: string,
    month: number,
    year: number
  ): Promise<{ message: string }> {
    const response = await apiClient.delete(
      `/api/v2/monthly-salary/employee/${employeeId}/month/${month}/year/${year}`
    );
    return response.data;
  }
}; 