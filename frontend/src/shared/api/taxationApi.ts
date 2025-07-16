import { BaseAPI } from './baseApi';
import * as Types from '../types/api';

// Type definitions for Taxation API
export interface TaxInputData {
  financial_year: string;
  basic_salary: number;
  hra: number;
  special_allowance: number;
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
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/salary`;
      return await this.baseApi.put(url, {
        employee_id: request.employee_id,
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
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/perquisites`;
      return await this.baseApi.put(url, {
        employee_id: request.employee_id,
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
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/deductions`;
      return await this.baseApi.put(url, {
        employee_id: request.employee_id,
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
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/house-property`;
      return await this.baseApi.put(url, {
        employee_id: request.employee_id,
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
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/capital-gains`;
      return await this.baseApi.put(url, {
        employee_id: request.employee_id,
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
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/retirement-benefits`;
      return await this.baseApi.put(url, {
        employee_id: request.employee_id,
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
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/other-income`;
      return await this.baseApi.put(url, {
        employee_id: request.employee_id,
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
      const url = `/api/v2/taxation/records/employee/${request.employee_id}/regime`;
      return await this.baseApi.put(url, {    
        employee_id: request.employee_id,
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
   * Check if regime update is allowed for an employee and tax year
   */
  async isRegimeUpdateAllowed(employee_id: string, tax_year: string): Promise<{ is_allowed: boolean; regime_type: 'old' | 'new'; message?: string }> {
    try {
      const url = `/api/v2/taxation/records/employee/${employee_id}/regime/allowed`;
      // Backend expects query parameters for GET request
      return await this.baseApi.get(url, { params: { tax_year } });
    } catch (error) {
      console.error('Error checking if regime update is allowed:', error);
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
      const url = `/api/v2/taxation/monthly-tax/employee/${employeeId}`;
      return await this.baseApi.get(url);
    } catch (error) {
      console.error('Error computing monthly tax:', error);
      throw error;
    }
  }

  /**
   * Export salary package data to Excel
   */
  async exportSalaryPackageToExcel(
    employeeId: string,
    taxYear?: string
  ): Promise<Blob> {
    try {
      const url = `/api/v2/taxation/export/salary-package/${employeeId}`;
      const params: Record<string, string> = {};
      if (taxYear) {
        params.tax_year = taxYear;
      }

      return await this.baseApi.download(url, { params });
    } catch (error) {
      console.error('Error exporting salary package to Excel:', error);
      throw error;
    }
  }

  /**
   * Export salary package data to Excel (single sheet)
   */
  async exportSalaryPackageSingleSheet(
    employeeId: string,
    taxYear?: string
  ): Promise<Blob> {
    try {
      const url = `/api/v2/taxation/export/salary-package-single/${employeeId}`;
      const params: Record<string, string> = {};
      if (taxYear) {
        params.tax_year = taxYear;
      }

      return await this.baseApi.download(url, { params });
    } catch (error) {
      console.error('Error exporting salary package to single Excel sheet:', error);
      throw error;
    }
  }

  /**
   * Process loan schedule for an employee
   * Get loan schedule with monthly payment breakdown, outstanding amounts, and interest calculations
   */
  async processLoanSchedule(
    employeeId: string,
    taxYear: string
  ): Promise<any> {
    try {
      return await this.baseApi.get(`/api/v2/taxation/loan-schedule/employee/${employeeId}?tax_year=${taxYear}`);
    } catch (error) {
      console.error('Error processing loan schedule:', error);
      throw error;
    }
  }
}

// Export singleton instance
const taxationApi = TaxationAPI.getInstance();
export default taxationApi; 