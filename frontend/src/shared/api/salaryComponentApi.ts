import axios, { AxiosInstance } from 'axios';

export interface SalaryComponent {
  component_id: string;
  code: string;
  name: string;
  component_type: 'EARNING' | 'DEDUCTION' | 'REIMBURSEMENT';
  value_type: 'FIXED' | 'FORMULA' | 'VARIABLE';
  is_taxable: boolean;
  exemption_section?: string;
  formula?: string;
  default_value?: number;
  calculation_order: number;
  description?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
  created_by?: string;
  updated_by?: string;
  category?: string;
  is_fixed?: boolean;
}

export interface GlobalSalaryComponent {
  component_id: string;
  code: string;
  name: string;
  component_type: string;
  value_type: string;
  is_taxable: boolean;
  exemption_section?: string;
  formula?: string;
  default_value?: number;
  description?: string;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ComponentAssignment {
  assignment_id: string;
  organization_id: string;
  component_id: string;
  component_name?: string;
  component_code?: string;
  status: 'ACTIVE' | 'INACTIVE' | 'PENDING';
  assigned_by: string;
  assigned_at: string;
  notes?: string;
  effective_from?: string;
  effective_to?: string;
  organization_specific_config: Record<string, any>;
  is_effective: boolean;
}

export interface AssignComponentsRequest {
  organization_id: string;
  component_ids: string[];
  status?: 'ACTIVE' | 'INACTIVE' | 'PENDING';
  notes?: string;
  effective_from?: string;
  effective_to?: string;
  organization_specific_config?: Record<string, any>;
}

export interface RemoveComponentsRequest {
  organization_id: string;
  component_ids: string[];
  notes?: string;
}

export interface AssignmentQueryRequest {
  organization_id?: string;
  component_id?: string;
  status?: string;
  include_inactive?: boolean;
  page?: number;
  page_size?: number;
}

export interface CreateSalaryComponentRequest {
  code: string;
  name: string;
  component_type: 'EARNING' | 'DEDUCTION' | 'REIMBURSEMENT';
  value_type: 'FIXED' | 'FORMULA' | 'VARIABLE';
  is_taxable: boolean;
  formula?: string;
  description?: string;
  is_active?: boolean;
}

export interface UpdateSalaryComponentRequest {
  code?: string;
  name?: string;
  component_type?: 'EARNING' | 'DEDUCTION' | 'REIMBURSEMENT';
  value_type?: 'FIXED' | 'FORMULA' | 'VARIABLE';
  is_taxable?: boolean;
  formula?: string;
  description?: string;
  is_active?: boolean;
}

export interface FormulaValidationRequest {
  formula: string;
  component_type: 'EARNING' | 'DEDUCTION' | 'REIMBURSEMENT';
}

export interface FormulaValidationResponse {
  is_valid: boolean;
  parsed_formula?: string;
  errors?: string[];
  warnings?: string[];
}

export interface SalaryComponentsListResponse {
  components: SalaryComponent[];
  total: number;
  page: number;
  limit: number;
}

export interface SalaryComponentFilters {
  component_type?: 'EARNING' | 'DEDUCTION' | 'REIMBURSEMENT';
  value_type?: 'FIXED' | 'FORMULA' | 'VARIABLE';
  is_taxable?: boolean;
  is_active?: boolean;
  search?: string;
  page?: number;
  limit?: number;
  category?: string;
}

export interface EmployeeSalaryMapping {
  employee_id: string;
  employee_name?: string;
  component_id: string;
  component_name?: string;
  fixed_amount?: number;
  percentage_of_basic?: number;
  effective_from: string;
  effective_to?: string;
  is_active: boolean;
}

export interface CreateEmployeeMappingRequest {
  employee_id: string;
  component_id: string;
  fixed_amount?: number;
  percentage_of_basic?: number;
  effective_from: string;
  effective_to?: string;
}

export class SalaryComponentAPI {
  private static instance: SalaryComponentAPI;
  private axiosInstance: AxiosInstance;

  private constructor() {
    // Create a separate axios instance for Salary Components API on port 8001
    const baseURL = process.env.REACT_APP_SALARY_API_URL || 'http://localhost:8001';
    
    this.axiosInstance = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'X-Platform': 'web',
        'X-Client-Version': process.env.REACT_APP_VERSION || '1.0.0',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor to add auth token
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error.response?.data || error);
      }
    );
  }

  public static getInstance(): SalaryComponentAPI {
    if (!SalaryComponentAPI.instance) {
      SalaryComponentAPI.instance = new SalaryComponentAPI();
    }
    return SalaryComponentAPI.instance;
  }

  // Salary Components CRUD operations
  async getSalaryComponents(filters?: SalaryComponentFilters): Promise<SalaryComponentsListResponse> {
    const queryParams = new URLSearchParams();
    
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }

    const url = `/api/v2/salary-components${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response: any = await this.axiosInstance.get(url);
    
    // Transform backend response to match frontend interface
    if (response.status === 'success' && response.data) {
      const backendData = response.data;
      return {
        components: (backendData.items || []).map((item: any) => this.transformBackendItemToFrontend(item)),
        total: backendData.total_count || 0,
        page: backendData.page || 1,
        limit: backendData.page_size || 10,
      };
    }
    
    // Fallback for unexpected response format
    return {
      components: [],
      total: 0,
      page: 1,
      limit: 10,
    };
  }

  private mapComponentTypeToCategory(componentType: string): string {
    switch (componentType) {
      case 'EARNING':
        return 'BASIC';
      case 'DEDUCTION':
        return 'DEDUCTION';
      case 'REIMBURSEMENT':
        return 'REIMBURSEMENT';
      default:
        return 'OTHER';
    }
  }

  private transformBackendItemToFrontend(item: any): SalaryComponent {
    return {
      component_id: item.id, // Map 'id' to 'component_id'
      code: item.code,
      name: item.name,
      component_type: item.component_type,
      value_type: item.value_type,
      is_taxable: item.is_taxable,
      exemption_section: item.exemption_section,
      formula: item.formula,
      default_value: item.default_value,
      description: item.description,
      is_active: item.is_active,
      created_at: item.created_at,
      updated_at: item.updated_at,
      created_by: item.created_by,
      updated_by: item.updated_by,
      calculation_order: 0, // Default value since not in backend
      category: this.mapComponentTypeToCategory(item.component_type),
    };
  }

  async getSalaryComponent(componentId: string): Promise<SalaryComponent> {
    const response: any = await this.axiosInstance.get(`/api/v2/salary-components/${componentId}`);
    
    // Transform backend response to match frontend interface
    if (response.status === 'success' && response.data) {
      return this.transformBackendItemToFrontend(response.data);
    }
    
    throw new Error('Failed to fetch salary component');
  }

  async createSalaryComponent(componentData: CreateSalaryComponentRequest): Promise<SalaryComponent> {
    const response: any = await this.axiosInstance.post('/api/v2/salary-components', componentData);
    
    // Transform backend response to match frontend interface
    if (response.status === 'success' && response.data) {
      return this.transformBackendItemToFrontend(response.data);
    }
    
    throw new Error('Failed to create salary component');
  }

  async updateSalaryComponent(componentId: string, componentData: UpdateSalaryComponentRequest): Promise<SalaryComponent> {
    const response: any = await this.axiosInstance.put(`/api/v2/salary-components/${componentId}`, componentData);
    
    // Transform backend response to match frontend interface
    if (response.status === 'success' && response.data) {
      return this.transformBackendItemToFrontend(response.data);
    }
    
    throw new Error('Failed to update salary component');
  }

  async deleteSalaryComponent(componentId: string): Promise<void> {
    await this.axiosInstance.delete(`/api/v2/salary-components/${componentId}`);
  }

  // Formula validation
  async validateFormula(formulaData: FormulaValidationRequest): Promise<FormulaValidationResponse> {
    return await this.axiosInstance.post('/api/v2/salary-components/validate-formula', formulaData);
  }

  // Employee mapping operations
  async getEmployeeMappings(employeeId?: string, componentId?: string): Promise<EmployeeSalaryMapping[]> {
    const queryParams = new URLSearchParams();
    if (employeeId) queryParams.append('employee_id', employeeId);
    if (componentId) queryParams.append('component_id', componentId);

    const url = `/api/v2/salary-components/employee-mappings${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return await this.axiosInstance.get(url);
  }

  async createEmployeeMapping(mappingData: CreateEmployeeMappingRequest): Promise<EmployeeSalaryMapping> {
    return await this.axiosInstance.post('/api/v2/salary-components/employee-mappings', mappingData);
  }

  async updateEmployeeMapping(mappingId: string, mappingData: Partial<CreateEmployeeMappingRequest>): Promise<EmployeeSalaryMapping> {
    return await this.axiosInstance.put(`/api/v2/salary-components/employee-mappings/${mappingId}`, mappingData);
  }

  async deleteEmployeeMapping(mappingId: string): Promise<void> {
    await this.axiosInstance.delete(`/api/v2/salary-components/employee-mappings/${mappingId}`);
  }

  // Calculation test endpoint
  async testCalculation(employeeId: string, componentId: string): Promise<{ calculated_amount: number; details: any }> {
    return await this.axiosInstance.post('/api/v2/salary-components/test-calculation', {
      employee_id: employeeId,
      component_id: componentId
    });
  }

  // ==================== ASSIGNMENT METHODS ====================

  async getGlobalSalaryComponents(params?: {
    search_term?: string;
    component_type?: string;
    is_active?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<{ data: GlobalSalaryComponent[]; total: number; success: boolean; message?: string }> {
    const response = await this.axiosInstance.get('/api/v2/salary-components/assignments/global', { params });
    return response.data;
  }

  async getOrganizationComponents(organizationId: string, includeInactive: boolean = false): Promise<{
    data: ComponentAssignment[];
    total: number;
    success: boolean;
    message?: string;
  }> {
    const response = await this.axiosInstance.get(`/api/v2/salary-components/assignments/organization/${organizationId}`, {
      params: { include_inactive: includeInactive }
    });
    return response.data;
  }

  async getAssignmentSummary(organizationId: string): Promise<{
    data: any;
    success: boolean;
    message?: string;
  }> {
    const response = await this.axiosInstance.get(`/api/v2/salary-components/assignments/organization/${organizationId}/summary`);
    return response.data;
  }

  async getComparisonData(organizationId: string): Promise<{
    data: {
      global_components: GlobalSalaryComponent[];
      organization_components: ComponentAssignment[];
      available_for_assignment: GlobalSalaryComponent[];
    };
    success: boolean;
    message?: string;
  }> {
    const response = await this.axiosInstance.get(`/api/v2/salary-components/assignments/organization/${organizationId}/comparison`);
    return response.data;
  }

  async assignComponents(request: AssignComponentsRequest): Promise<{
    data: ComponentAssignment[];
    success: boolean;
    message?: string;
  }> {
    const response = await this.axiosInstance.post('/api/v2/salary-components/assignments/assign', request);
    return response.data;
  }

  async removeComponents(request: RemoveComponentsRequest): Promise<{
    data: ComponentAssignment[];
    success: boolean;
    message?: string;
  }> {
    const response = await this.axiosInstance.post('/api/v2/salary-components/assignments/remove', request);
    return response.data;
  }

  async searchAssignments(params: AssignmentQueryRequest): Promise<{
    data: ComponentAssignment[];
    total: number;
    success: boolean;
    message?: string;
  }> {
    const response = await this.axiosInstance.get('/api/v2/salary-components/assignments/search', { params });
    return response.data;
  }

  async updateAssignment(request: {
    assignment_id: string;
    status?: string;
    notes?: string;
    effective_from?: string;
    effective_to?: string;
    organization_specific_config?: Record<string, any>;
  }): Promise<{
    data: ComponentAssignment;
    success: boolean;
    message?: string;
  }> {
    const response = await this.axiosInstance.put('/api/v2/salary-components/assignments/update', request);
    return response.data;
  }

  // ==================== HEALTH CHECK ====================

  async healthCheck(): Promise<{ success: boolean; message?: string }> {
    const response = await this.axiosInstance.get('/api/v2/salary-components/assignments/health');
    return response.data;
  }
}

export const salaryComponentApi = SalaryComponentAPI.getInstance(); 