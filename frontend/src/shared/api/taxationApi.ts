import { BaseAPI } from './baseApi';
import * as Types from '../types/api';

// Type definitions for Taxation API
export interface TaxInputData {
  financial_year: string;
  basic_salary: number;
  hra: number;
  special_allowance: number;
  bonus: number;
  other_allowances: number;
  // Deductions
  pf_contribution: number;
  professional_tax: number;
  tds: number;
  // Tax Saving Investments
  section_80c: number;
  section_80d: number;
  nps_contribution: number;
  // Personal Details
  age: number;
  is_senior_citizen: boolean;
  metro_city: boolean;
  // Tax Regime
  tax_regime: 'old' | 'new';
}

export interface TaxCalculationResult {
  gross_salary: number;
  total_deductions: number;
  taxable_income: number;
  tax_liability: number;
  cess_amount: number;
  surcharge_amount: number;
  total_tax: number;
  net_salary: number;
  monthly_net_salary: number;
  effective_tax_rate: number;
  tax_breakdown: {
    income_tax: number;
    surcharge: number;
    cess: number;
  };
  regime_comparison?: {
    old_regime: TaxCalculationResult;
    new_regime: TaxCalculationResult;
    recommended_regime: 'old' | 'new';
    savings_amount: number;
  };
}

export interface TaxOptimizationSuggestion {
  type: 'section_80c' | 'section_80d' | 'nps' | 'regime_switch';
  title: string;
  description: string;
  current_amount: number;
  suggested_amount: number;
  potential_savings: number;
  priority: 'high' | 'medium' | 'low';
  implementation_effort: 'easy' | 'moderate' | 'complex';
}

export interface TaxOptimizationResponse {
  current_tax: number;
  optimized_tax: number;
  total_savings: number;
  suggestions: TaxOptimizationSuggestion[];
  recommended_regime: 'old' | 'new';
}

export interface TaxAnalytics {
  financial_year: string;
  total_records: number;
  average_tax_rate: number;
  total_tax_liability: number;
  tax_distribution: {
    regime: 'old' | 'new';
    count: number;
    percentage: number;
  }[];
  monthly_breakdown: {
    month: string;
    records_count: number;
    total_tax: number;
  }[];
}

/**
 * Comprehensive Taxation API service
 * Handles all taxation-related operations including calculations, records, and optimization
 */
class TaxationAPI {
  private static instance: TaxationAPI;
  private baseApi: BaseAPI;

  private constructor() {
    this.baseApi = BaseAPI.getInstance();
  }

  public static getInstance(): TaxationAPI {
    if (!TaxationAPI.instance) {
      TaxationAPI.instance = new TaxationAPI();
    }
    return TaxationAPI.instance;
  }

  // =============================================================================
  // COMPREHENSIVE TAX CALCULATION ENDPOINTS
  // =============================================================================

  /**
   * Calculate comprehensive tax including all income sources and components (generic calculation)
   * Use this for tax calculations without database operations
   */
  async calculateComprehensiveTax(
    input: Types.ComprehensiveTaxInputDTO
  ): Promise<Types.PeriodicTaxCalculationResponseDTO> {
    try {
      return await this.baseApi.post('/api/v2/taxation/calculate-comprehensive', input);
    } catch (error) {
      console.error('Error calculating comprehensive tax:', error);
      throw error;
    }
  }

  /**
   * Calculate comprehensive tax for a specific employee and update their taxation record in database
   * Use this for employee-specific calculations with database operations
   */
  async calculateComprehensiveTaxForEmployee(
    employeeId: string,
    input: Types.ComprehensiveTaxInputDTO
  ): Promise<Types.PeriodicTaxCalculationResponseDTO> {
    try {
      return await this.baseApi.post(`/api/v2/taxation/records/employee/${employeeId}/calculate-comprehensive`, input);
    } catch (error) {
      console.error('Error calculating comprehensive tax for employee:', error);
      throw error;
    }
  }

  // =============================================================================
  // COMPONENT-SPECIFIC CALCULATION ENDPOINTS
  // =============================================================================

  /**
   * Calculate perquisites tax impact only
   */
  async calculatePerquisites(
    perquisites: Types.PerquisitesDTO,
    regimeType: Types.TaxRegime
  ): Promise<any> {
    try {
      return await this.baseApi.post(
        `/api/v2/taxation/perquisites/calculate?regime_type=${regimeType}`,
        perquisites
      );
    } catch (error) {
      console.error('Error calculating perquisites:', error);
      throw error;
    }
  }

  /**
   * Calculate house property income tax impact only
   */
  async calculateHouseProperty(
    houseProperty: Types.HousePropertyIncomeDTO,
    regimeType: Types.TaxRegime
  ): Promise<any> {
    try {
      return await this.baseApi.post(
        `/api/v2/taxation/house-property/calculate?regime_type=${regimeType}`,
        houseProperty
      );
    } catch (error) {
      console.error('Error calculating house property:', error);
      throw error;
    }
  }

  /**
   * Calculate capital gains tax impact only
   */
  async calculateCapitalGains(
    capitalGains: Types.CapitalGainsIncomeDTO,
    regimeType: Types.TaxRegime
  ): Promise<any> {
    try {
      return await this.baseApi.post(
        `/api/v2/taxation/capital-gains/calculate?regime_type=${regimeType}`,
        capitalGains
      );
    } catch (error) {
      console.error('Error calculating capital gains:', error);
      throw error;
    }
  }

  // =============================================================================
  // UTILITY AND INFORMATION ENDPOINTS
  // =============================================================================

  /**
   * Get tax regime comparison information
   */
  async getTaxRegimeComparison(): Promise<any> {
    try {
      return await this.baseApi.get('/api/v2/taxation/regime-comparison');
    } catch (error) {
      console.error('Error fetching tax regime comparison:', error);
      throw error;
    }
  }

  /**
   * Get available tax years
   */
  async getAvailableTaxYears(): Promise<Types.TaxYearInfoDTO[]> {
    try {
      return await this.baseApi.get('/api/v2/taxation/tax-years');
    } catch (error) {
      console.error('Error fetching available tax years:', error);
      throw error;
    }
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<Types.HealthCheckResponse> {
    try {
      return await this.baseApi.get('/api/v2/taxation/health');
    } catch (error) {
      console.error('Error checking taxation service health:', error);
      throw error;
    }
  }

  // =============================================================================
  // EMPLOYEE SELECTION ENDPOINTS
  // =============================================================================

  /**
   * Get employees for selection with filtering and pagination
   */
  async getEmployeesForSelection(
    query?: Types.EmployeeSelectionQuery
  ): Promise<Types.EmployeeSelectionResponse> {
    try {
      const params = new URLSearchParams();
      if (query) {
        Object.entries(query).forEach(([key, value]) => {
          if (value !== undefined && value !== null) {
            params.append(key, value.toString());
          }
        });
      }

      const url = `/api/v2/taxation/employees/selection${params.toString() ? `?${params.toString()}` : ''}`;
      return await this.baseApi.get(url);
    } catch (error) {
      console.error('Error fetching employees for selection:', error);
      throw error;
    }
  }

  // =============================================================================
  // LEGACY TAX CALCULATION ENDPOINTS (for backward compatibility)
  // =============================================================================

  /**
   * Calculate tax for given input data
   */
  async calculateTax(inputData: TaxInputData): Promise<TaxCalculationResult> {
    try {
      const response = await this.baseApi.post<TaxCalculationResult>('/api/v2/taxation/calculate', inputData);
      return response;
    } catch (error: any) {
      console.error('Error calculating tax:', error);
      throw new Error(error.response?.data?.detail || 'Failed to calculate tax');
    }
  }

  /**
   * Calculate tax for both regimes and compare
   */
  async calculateTaxComparison(inputData: Omit<TaxInputData, 'tax_regime'>): Promise<TaxCalculationResult> {
    try {
      const response = await this.baseApi.post<TaxCalculationResult>('/api/v2/taxation/calculate/compare', inputData);
      return response;
    } catch (error: any) {
      console.error('Error calculating tax comparison:', error);
      throw new Error(error.response?.data?.detail || 'Failed to calculate tax comparison');
    }
  }

  /**
   * Get tax optimization suggestions
   */
  async getOptimizationSuggestions(inputData: TaxInputData): Promise<TaxOptimizationResponse> {
    try {
      const response = await this.baseApi.post<TaxOptimizationResponse>('/api/v2/taxation/optimize', inputData);
      return response;
    } catch (error: any) {
      console.error('Error getting optimization suggestions:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get optimization suggestions');
    }
  }

  // =============================================================================
  // TEMPLATE AND UTILITY ENDPOINTS
  // =============================================================================

  /**
   * Get tax calculation templates
   */
  async getTaxTemplates(): Promise<{ templates: TaxInputData[] }> {
    try {
      const response = await this.baseApi.get<{ templates: TaxInputData[] }>('/api/v2/taxation/templates');
      return response;
    } catch (error: any) {
      console.error('Error fetching tax templates:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch tax templates');
    }
  }

  /**
   * Save tax calculation template
   */
  async saveTaxTemplate(templateData: TaxInputData & { name: string }): Promise<{ message: string }> {
    try {
      const response = await this.baseApi.post<{ message: string }>('/api/v2/taxation/templates', templateData);
      return response;
    } catch (error: any) {
      console.error('Error saving tax template:', error);
      throw new Error(error.response?.data?.detail || 'Failed to save tax template');
    }
  }

  /**
   * Get current financial year information
   */
  async getCurrentFinancialYear(): Promise<{ financial_year: string; start_date: string; end_date: string }> {
    try {
      const response = await this.baseApi.get<{ financial_year: string; start_date: string; end_date: string }>('/api/v2/taxation/current-financial-year');
      return response;
    } catch (error: any) {
      console.error('Error fetching current financial year:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch current financial year');
    }
  }

  /**
   * Get tax slabs for a specific financial year and regime
   */
  async getTaxSlabs(financialYear: string, regime: 'old' | 'new'): Promise<{
    financial_year: string;
    regime: string;
    slabs: Array<{
      min_income: number;
      max_income: number | null;
      tax_rate: number;
    }>;
  }> {
    try {
      const response = await this.baseApi.get(`/api/v2/taxation/slabs?financial_year=${financialYear}&regime=${regime}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching tax slabs:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch tax slabs');
    }
  }

  // =============================================================================
  // LEGACY ENDPOINTS (for backward compatibility)
  // =============================================================================

  /**
   * Get all taxation records (legacy endpoint)
   */
  async getAllTaxation(taxYear?: string | null, filingStatus?: string | null): Promise<any> {
    try {
      const params: Record<string, string> = {};
      if (taxYear) params.financial_year = taxYear;
      if (filingStatus) params.filing_status = filingStatus;

      const response = await this.baseApi.get('/api/v2/taxation/records', { params });
      return response;
    } catch (error: any) {
      console.error('Error fetching all taxation:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch taxation records');
    }
  }

  /**
   * Get my taxation records (legacy endpoint)
   */
  async getMyTaxation(): Promise<any> {
    try {
      const response = await this.baseApi.get('/api/v2/taxation/records/my');
      return response;
    } catch (error: any) {
      console.error('Error fetching my taxation:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch my taxation records');
    }
  }

  // =============================================================================
  // COMPONENT MANAGEMENT ENDPOINTS
  // =============================================================================

  /**
   * Get specific component data for an employee
   */
  async getComponent(
    employeeId: string,
    taxYear: string,
    componentType: string
  ): Promise<Types.ComponentResponse> {
    try {
      const url = `/api/v2/taxation/records/employee/${employeeId}/component/${componentType}?tax_year=${taxYear}`;
      return await this.baseApi.get(url);
    } catch (error) {
      console.error('Error fetching component:', error);
      throw error;
    }
  }

  /**
   * Update salary component for an employee
   */
  async updateSalaryComponent(
    request: {
      employee_id: string;
      tax_year: string;
      salary_income: any;
      notes?: string;
    }
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/component/salary_income`;
      return await this.baseApi.patch(url, {
        tax_year: request.tax_year,
        salary_income: request.salary_income,
        notes: request.notes
      });
    } catch (error) {
      console.error('Error updating salary component:', error);
      throw error;
    }
  }

  /**
   * Update perquisites component for an employee
   */
  async updatePerquisitesComponent(
    request: {
      employee_id: string;
      tax_year: string;
      perquisites: any;
      notes?: string;
    }
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/component/perquisites`;
      return await this.baseApi.patch(url, {
        tax_year: request.tax_year,
        perquisites: request.perquisites,
        notes: request.notes
      });
    } catch (error) {
      console.error('Error updating perquisites component:', error);
      throw error;
    }
  }

  /**
   * Update deductions component for an employee
   */
  async updateDeductionsComponent(
    request: {
      employee_id: string;
      tax_year: string;
      deductions: any;
      notes?: string;
    }
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/component/deductions`;
      return await this.baseApi.patch(url, {
        tax_year: request.tax_year,
        deductions: request.deductions,
        notes: request.notes
      });
    } catch (error) {
      console.error('Error updating deductions component:', error);
      throw error;
    }
  }

  /**
   * Update house property component for an employee
   */
  async updateHousePropertyComponent(
    request: {
      employee_id: string;
      tax_year: string;
      house_property_income: any;
      notes?: string;
    }
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/component/house_property_income`;
      return await this.baseApi.patch(url, {
        tax_year: request.tax_year,
        house_property_income: request.house_property_income,
        notes: request.notes
      });
    } catch (error) {
      console.error('Error updating house property component:', error);
      throw error;
    }
  }

  /**
   * Update capital gains component for an employee
   */
  async updateCapitalGainsComponent(
    request: {
      employee_id: string;
      tax_year: string;
      capital_gains_income: any;
      notes?: string;
    }
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/component/capital_gains_income`;
      return await this.baseApi.patch(url, {
        tax_year: request.tax_year,
        capital_gains_income: request.capital_gains_income,
        notes: request.notes
      });
    } catch (error) {
      console.error('Error updating capital gains component:', error);
      throw error;
    }
  }

  /**
   * Update retirement benefits component for an employee
   */
  async updateRetirementBenefitsComponent(
    request: {
      employee_id: string;
      tax_year: string;
      retirement_benefits: any;
      notes?: string;
    }
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/component/retirement_benefits`;
      return await this.baseApi.patch(url, {
        tax_year: request.tax_year,
        retirement_benefits: request.retirement_benefits,
        notes: request.notes
      });
    } catch (error) {
      console.error('Error updating retirement benefits component:', error);
      throw error;
    }
  }

  /**
   * Update other income component for an employee
   */
  async updateOtherIncomeComponent(
    request: {
      employee_id: string;
      tax_year: string;
      other_income: any;
      notes?: string;
    }
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/component/other_income`;
      return await this.baseApi.patch(url, {
        tax_year: request.tax_year,
        other_income: request.other_income,
        notes: request.notes
      });
    } catch (error) {
      console.error('Error updating other income component:', error);
      throw error;
    }
  }

  /**
   * Update monthly payroll component for an employee
   */
  async updateMonthlyPayrollComponent(
    request: {
      employee_id: string;
      tax_year: string;
      monthly_payroll: any;
      notes?: string;
    }
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/component/monthly_payroll`;
      return await this.baseApi.patch(url, {
        tax_year: request.tax_year,
        monthly_payroll: request.monthly_payroll,
        notes: request.notes
      });
    } catch (error) {
      console.error('Error updating monthly payroll component:', error);
      throw error;
    }
  }

  /**
   * Update regime component for an employee
   */
  async updateRegimeComponent(
    request: {
      employee_id: string;
      tax_year: string;
      regime_type: string;
      age: number;
      notes?: string;
    }
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/component/regime`;
      return await this.baseApi.patch(url, {
        tax_year: request.tax_year,
        regime_type: request.regime_type,
        age: request.age,
        notes: request.notes
      });
    } catch (error) {
      console.error('Error updating regime component:', error);
      throw error;
    }
  }

  /**
   * Get taxation record status for an employee
   */
  async getTaxationRecordStatus(
    employeeId: string,
    taxYear: string
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${employeeId}/status?tax_year=${taxYear}`;
      return await this.baseApi.get(url);
    } catch (error) {
      console.error('Error fetching taxation record status:', error);
      throw error;
    }
  }

  // =============================================================================
  // MONTHLY TAX COMPUTATION ENDPOINTS
  // =============================================================================

  /**
   * Compute monthly tax for an employee
   */
  async computeMonthlyTax(
    employeeId: string,
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${employeeId}/compute-monthly-tax`;
      return await this.baseApi.post(url);
    } catch (error) {
      console.error('Error computing monthly tax:', error);
      throw error;
    }
  }

  /**
   * Compute monthly tax for a specific month and year
   */
  async computeMonthlyTaxSimple(
    employeeId: string,
    month: number,
    year: number
  ): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${employeeId}/compute-monthly-tax-simple`;
      return await this.baseApi.post(url, { month, year });
    } catch (error) {
      console.error('Error computing monthly tax simple:', error);
      throw error;
    }
  }

  /**
   * Compute current month tax for an employee
   */
  async computeCurrentMonthTax(employeeId: string): Promise<any> {
    try {
      const url = `/api/v2/taxation/records/employee/${employeeId}/compute-current-month-tax`;
      return await this.baseApi.post(url);
    } catch (error) {
      console.error('Error computing current month tax:', error);
      throw error;
    }
  }
}

// Export singleton instance
const taxationApi = TaxationAPI.getInstance();
export default taxationApi; 