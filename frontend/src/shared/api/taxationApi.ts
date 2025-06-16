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

export interface TaxRecord {
  id: string;
  employee_id: string;
  financial_year: string;
  tax_input_data: TaxInputData;
  calculation_result: TaxCalculationResult;
  created_at: string;
  updated_at: string;
  is_finalized: boolean;
  notes?: string;
}

export interface TaxRecordFilters {
  skip?: number;
  limit?: number;
  financial_year?: string;
  employee_id?: string;
  is_finalized?: boolean;
  search?: string;
}

export interface TaxRecordListResponse {
  total: number;
  records: TaxRecord[];
  skip: number;
  limit: number;
}

export interface CreateTaxRecordRequest {
  employee_id: string;
  financial_year: string;
  tax_input_data: TaxInputData;
  notes?: string;
}

export interface UpdateTaxRecordRequest {
  tax_input_data?: Partial<TaxInputData>;
  notes?: string;
  is_finalized?: boolean;
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
   * Calculate house property income tax
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
      console.error('Error calculating house property income:', error);
      throw error;
    }
  }

  /**
   * Calculate capital gains tax
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
  // RECORD MANAGEMENT ENDPOINTS
  // =============================================================================

  /**
   * Create a new taxation record
   */
  async createRecord(
    request: Types.CreateTaxationRecordRequest
  ): Promise<Types.CreateTaxationRecordResponse> {
    try {
      return await this.baseApi.post('/api/v2/taxation/records', request);
    } catch (error) {
      console.error('Error creating taxation record:', error);
      throw error;
    }
  }

  /**
   * Get list of taxation records with optional filters
   */
  async listRecords(
    query?: Types.TaxationRecordQuery
  ): Promise<Types.TaxationRecordListResponse> {
    try {
      const params = query ? new URLSearchParams(
        Object.entries(query).reduce((acc, [key, value]) => {
          if (value !== undefined && value !== null) {
            acc[key] = value.toString();
          }
          return acc;
        }, {} as Record<string, string>)
      ) : undefined;

      const url = params ? `/api/v2/taxation/records?${params}` : '/api/v2/taxation/records';
      return await this.baseApi.get<Types.TaxationRecordListResponse>(url);
    } catch (error) {
      console.error('Error listing taxation records:', error);
      throw error;
    }
  }

  /**
   * Get taxation record by ID
   */
  async getRecord(taxationId: string): Promise<Types.TaxationRecordSummaryDTO> {
    try {
      return await this.baseApi.get<Types.TaxationRecordSummaryDTO>(`/api/v2/taxation/records/${taxationId}`);
    } catch (error) {
      console.error('Error getting taxation record:', error);
      throw error;
    }
  }

  // =============================================================================
  // INFORMATION AND UTILITY ENDPOINTS
  // =============================================================================

  /**
   * Get comparison between old and new tax regimes
   */
  async getTaxRegimeComparison(): Promise<any> {
    try {
      return await this.baseApi.get('/api/v2/taxation/tax-regimes/comparison');
    } catch (error) {
      console.error('Error getting tax regime comparison:', error);
      throw error;
    }
  }

  /**
   * Get available tax years for selection
   */
  async getAvailableTaxYears(): Promise<Types.TaxYearInfoDTO[]> {
    try {
      return await this.baseApi.get('/api/v2/taxation/tax-years');
    } catch (error) {
      console.error('Error getting available tax years:', error);
      throw error;
    }
  }

  /**
   * Check taxation service health
   */
  async healthCheck(): Promise<Types.HealthCheckResponse> {
    try {
      return await this.baseApi.get('/api/v2/taxation/health');
    } catch (error) {
      console.error('Error checking taxation service health:', error);
      throw error;
    }
  }

  /**
   * Get employees for selection in taxation module
   */
  async getEmployeesForSelection(
    query?: Types.EmployeeSelectionQuery
  ): Promise<Types.EmployeeSelectionResponse> {
    try {
      const params = new URLSearchParams();
      
      if (query?.skip !== undefined) params.append('skip', query.skip.toString());
      if (query?.limit !== undefined) params.append('limit', query.limit.toString());
      if (query?.search) params.append('search', query.search);
      if (query?.department) params.append('department', query.department);
      if (query?.role) params.append('role', query.role);
      if (query?.status) params.append('status', query.status);
      if (query?.has_tax_record !== undefined) params.append('has_tax_record', query.has_tax_record.toString());
      if (query?.tax_year) params.append('tax_year', query.tax_year);

      const url = `/api/v2/taxation/employee-selection${params.toString() ? `?${params.toString()}` : ''}`;
      return await this.baseApi.get(url);
    } catch (error) {
      console.error('Error fetching employees for selection:', error);
      throw error;
    }
  }

  /**
   * Get detailed taxation record by employee ID
   */
  async getEmployeeTaxationRecord(
    employeeId: string,
    taxYear?: string
  ): Promise<Types.TaxationRecordSummaryDTO> {
    try {
      const params = new URLSearchParams();
      if (taxYear) params.append('tax_year', taxYear);

      const url = `/api/v2/taxation/records/employee/${employeeId}${params.toString() ? `?${params.toString()}` : ''}`;
      return await this.baseApi.get(url);
    } catch (error) {
      console.error('Error fetching employee taxation record:', error);
      throw error;
    }
  }

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

  /**
   * Create new tax record
   */
  async createTaxRecord(recordData: CreateTaxRecordRequest): Promise<TaxRecord> {
    try {
      const response = await this.baseApi.post<TaxRecord>('/api/v2/taxation/records', recordData);
      return response;
    } catch (error: any) {
      console.error('Error creating tax record:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create tax record');
    }
  }

  /**
   * Get list of tax records with filtering and pagination
   */
  async getTaxRecords(filters: TaxRecordFilters = {}): Promise<TaxRecordListResponse> {
    try {
      const {
        skip = 0,
        limit = 10,
        financial_year,
        employee_id,
        is_finalized,
        search
      } = filters;

      const params: Record<string, any> = {
        skip,
        limit
      };

      if (financial_year) params.financial_year = financial_year;
      if (employee_id) params.employee_id = employee_id;
      if (is_finalized !== undefined) params.is_finalized = is_finalized;
      if (search) params.search = search;

      const response = await this.baseApi.get<TaxRecordListResponse>('/api/v2/taxation/records', { params });
      return response;
    } catch (error: any) {
      console.error('Error fetching tax records:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch tax records');
    }
  }

  /**
   * Get tax record by ID
   */
  async getTaxRecordById(recordId: string): Promise<TaxRecord> {
    try {
      const response = await this.baseApi.get<TaxRecord>(`/api/v2/taxation/records/${recordId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching tax record:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch tax record');
    }
  }

  /**
   * Update tax record
   */
  async updateTaxRecord(recordId: string, updateData: UpdateTaxRecordRequest): Promise<TaxRecord> {
    try {
      const response = await this.baseApi.patch<TaxRecord>(`/api/v2/taxation/records/${recordId}`, updateData);
      return response;
    } catch (error: any) {
      console.error('Error updating tax record:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update tax record');
    }
  }

  /**
   * Delete tax record
   */
  async deleteTaxRecord(recordId: string): Promise<{ message: string }> {
    try {
      const response = await this.baseApi.delete<{ message: string }>(`/api/v2/taxation/records/${recordId}`);
      return response;
    } catch (error: any) {
      console.error('Error deleting tax record:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete tax record');
    }
  }

  /**
   * Finalize tax record (make it immutable)
   */
  async finalizeTaxRecord(recordId: string): Promise<TaxRecord> {
    try {
      const response = await this.baseApi.patch<TaxRecord>(`/api/v2/taxation/records/${recordId}/finalize`);
      return response;
    } catch (error: any) {
      console.error('Error finalizing tax record:', error);
      throw new Error(error.response?.data?.detail || 'Failed to finalize tax record');
    }
  }

  /**
   * Get tax analytics for dashboard
   */
  async getTaxAnalytics(financialYear?: string): Promise<TaxAnalytics> {
    try {
      const params = financialYear ? { financial_year: financialYear } : {};
      const response = await this.baseApi.get<TaxAnalytics>('/api/v2/taxation/analytics', { params });
      return response;
    } catch (error: any) {
      console.error('Error fetching tax analytics:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch tax analytics');
    }
  }

  /**
   * Export tax records to PDF/Excel
   */
  async exportTaxRecords(
    format: 'pdf' | 'excel',
    filters: TaxRecordFilters = {}
  ): Promise<Blob> {
    try {
      const params = { ...filters, format };
      const response = await this.baseApi.download('/api/v2/taxation/records/export', { params });
      return response;
    } catch (error: any) {
      console.error('Error exporting tax records:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export tax records');
    }
  }

  /**
   * Import tax records from file
   */
  async importTaxRecords(file: File): Promise<{ message: string; imported_count: number; errors?: any[] }> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.baseApi.upload<{ message: string; imported_count: number; errors?: any[] }>(
        '/api/v2/taxation/records/import',
        formData
      );
      return response;
    } catch (error: any) {
      console.error('Error importing tax records:', error);
      throw new Error(error.response?.data?.detail || 'Failed to import tax records');
    }
  }

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
   * Save tax calculation as template
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
      const response = await this.baseApi.get<{ financial_year: string; start_date: string; end_date: string }>(
        '/api/v2/taxation/financial-year/current'
      );
      return response;
    } catch (error: any) {
      console.error('Error fetching current financial year:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch current financial year');
    }
  }

  /**
   * Get tax slabs for a specific financial year
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
        const response = await this.baseApi.get(`/api/v2/taxation/tax-slabs`, {
        params: { financial_year: financialYear, regime }
      });
      return response;
    } catch (error: any) {
      console.error('Error fetching tax slabs:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch tax slabs');
    }
  }

  /**
   * Get all taxation data (admin only)
   */
  async getAllTaxation(taxYear?: string | null, filingStatus?: string | null): Promise<any> {
    try {
      const params = new URLSearchParams();
      if (taxYear) params.append('tax_year', taxYear);
      if (filingStatus) params.append('filing_status', filingStatus);
      
      const queryString = params.toString();
      const url = queryString ? `/api/v2/taxation/all?${queryString}` : '/api/v2/taxation/all';
      
      return await this.baseApi.get(url);
    } catch (error: any) {
      console.error('Error getting all taxation data:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get all taxation data');
    }
  }

  /**
   * Get current user's taxation data
   */
  async getMyTaxation(): Promise<any> {
    try {
      return await this.baseApi.get('/api/v2/taxation/my');
    } catch (error: any) {
      console.error('Error getting my taxation data:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get my taxation data');
    }
  }
}

// Export singleton instance
export const taxationApi = TaxationAPI.getInstance();
export default taxationApi; 