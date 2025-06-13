import { BaseAPI } from '../api/baseApi';
import { apiClient } from '../api';

// Backward compatibility service for payouts
export interface Payout {
  id: string;
  pay_period_start: string;
  pay_period_end: string;
  total_employees: number;
  total_amount: number;
  status: string;
  payout_date: string;
  // Salary components
  basic_salary: number;
  hra: number;
  da: number;
  medical_allowance: number;
  transport_allowance: number;
  other_allowances: number;
  bonus: number;
  reimbursements: number;
  // Deductions
  pf: number;
  esi: number;
  tds: number;
  other_deductions: number;
  // Totals
  gross_salary: number;
  total_deductions: number;
  net_salary: number;
  employees?: Array<{
    id: string;
    name: string;
    department: string;
    gross_salary: number;
    total_deductions: number;
    net_salary: number;
  }>;
}

export interface PayslipData {
  company_name: string;
  company_address: string;
  employee_name: string;
  employee_code: string;
  department: string;
  designation: string;
  pan_number: string;
  uan_number: string;
  pay_period: string;
  payout_date: string;
  days_in_month: number;
  days_worked: number;
  tax_regime: string;
  ytd_gross: number;
  ytd_tax_deducted: number;
  earnings: Record<string, number>;
  deductions: Record<string, number>;
  total_earnings: number;
  total_deductions: number;
  net_pay: number;
}

class PayoutService {
  private baseApi: BaseAPI;

  constructor() {
    this.baseApi = BaseAPI.getInstance();
  }

  // Add payout service methods here as needed
  async getPayslips(employeeId?: string) {
    try {
      const params = employeeId ? { employee_id: employeeId } : {};
      return await this.baseApi.get('/api/v2/payouts/payslips', { params });
    } catch (error) {
      console.error('Error fetching payslips:', error);
      throw error;
    }
  }

  async getSalaryDetails(employeeId?: string) {
    try {
      const params = employeeId ? { employee_id: employeeId } : {};
      return await this.baseApi.get('/api/v2/payouts/salary-details', { params });
    } catch (error) {
      console.error('Error fetching salary details:', error);
      throw error;
    }
  }

  async getPayoutReports(filters: any = {}) {
    try {
      return await this.baseApi.get('/api/v2/payouts/reports', { params: filters });
    } catch (error) {
      console.error('Error fetching payout reports:', error);
      throw error;
    }
  }

  async getAllPayouts(filters: any = {}) {
    try {
      return await this.baseApi.get('/api/v2/payouts', { params: filters });
    } catch (error) {
      console.error('Error fetching all payouts:', error);
      throw error;
    }
  }

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

  formatDateRange(start: string, end: string): string {
    return `${this.formatDate(start)} - ${this.formatDate(end)}`;
  }

  formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  }

  async getPayslipData(payoutId: string): Promise<PayslipData> {
    const response = await apiClient.get(`/api/v2/payouts/${payoutId}/payslip`);
    return response.data;
  }

  async downloadPayslip(payoutId: string): Promise<void> {
    const response = await apiClient.get(`/api/v2/payouts/${payoutId}/payslip/download`, {
      responseType: 'blob'
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `payslip-${payoutId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  async processMonthlyPayouts(year: number, month: number): Promise<void> {
    await apiClient.post('/api/v2/payouts/process', { year, month });
  }

  // Mock implementation for calculateMonthlyPayout
  async calculateMonthlyPayout(employeeId: string, month: number | null, year: number): Promise<any> {
    console.log(`Calculating monthly payout for employee ${employeeId} for ${month}/${year}`);
    // This would need to be implemented with actual calculation API
    return {
      employee_id: employeeId,
      basic_salary: 50000,
      da: 5000,
      hra: 15000,
      special_allowance: 10000,
      bonus: 0,
      transport_allowance: 2000,
      medical_allowance: 1500,
      other_allowances: 0,
      reimbursements: 0,
      epf_employee: 1800,
      esi_employee: 150,
      professional_tax: 200,
      tds: 5000,
      advance_deduction: 0,
      loan_deduction: 0,
      other_deductions: 0,
      gross_salary: 83500,
      total_deductions: 7150,
      net_salary: 76350,
      tax_regime: 'new',
      annual_tax_liability: 60000,
      pay_period_start: `${year}-${month?.toString().padStart(2, '0')}-01`,
      pay_period_end: `${year}-${month?.toString().padStart(2, '0')}-31`
    };
  }

  // Mock implementation for createPayout
  async createPayout(payoutData: any): Promise<any> {
    console.log('Creating payout:', payoutData);
    // This would need to be implemented with actual payout creation API
    return {
      id: `payout_${Date.now()}`,
      ...payoutData,
      status: 'created',
      created_at: new Date().toISOString()
    };
  }
}

const payoutService = new PayoutService();
export default payoutService; 