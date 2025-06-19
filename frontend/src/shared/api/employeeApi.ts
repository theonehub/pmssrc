import { BaseAPI } from './baseApi';

// Type definitions for Employee API
export interface Employee {
  employee_id: string;
  name: string;
  email: string;
  mobile?: string;
  gender?: string;
  date_of_birth?: string;
  date_of_joining?: string;
  role: string;
  department?: string;
  designation?: string;
  manager_id?: string;
  address?: string;
  emergency_contact?: string;
  blood_group?: string;
  location?: string;
  pan_number?: string;
  aadhar_number?: string;
  uan_number?: string;
  esi_number?: string;
  created_at?: string;
  updated_at?: string;
  is_active: boolean;
  status: string;
  profile_picture_url?: string;
  pan_document_path?: string;
  aadhar_document_path?: string;
  photo_path?: string;
  // Bank Details
  bank_account_number?: string;
  bank_name?: string;
  ifsc_code?: string;
  account_holder_name?: string;
  branch_name?: string;
  account_type?: string;
  // Leave Balance
  leave_balance?: {
    casual_leaves: number;
    sick_leaves: number;
    earned_leaves: number;
    total_leaves: number;
  };
  // Salary Information
  salary_info?: {
    basic_salary: number;
    hra: number;
    special_allowance: number;
    gross_salary: number;
    pf_contribution: number;
    professional_tax: number;
    net_salary: number;
  };
}

export interface EmployeeFilters {
  skip?: number;
  limit?: number;
  include_inactive?: boolean;
  include_deleted?: boolean;
  organisation_id?: string | null;
  search?: string;
  department?: string;
  role?: string;
  manager_id?: string;
  designation?: string;
  location?: string;
  // Date filters
  doj_from?: string;
  doj_to?: string;
  dol_from?: string;
  dol_to?: string;
  dob_from?: string;
  dob_to?: string;
  // Export specific fields
  fields?: string[];
  format?: string;
}

export interface EmployeeListResponse {
  total: number;
  employees: Employee[];
  skip: number;
  limit: number;
}

export interface CreateEmployeeRequest extends Omit<Employee, 'created_at' | 'updated_at' | 'employee_id'> {
  password: string;
}

export interface UpdateEmployeeRequest extends Partial<Omit<Employee, 'employee_id' | 'created_at' | 'updated_at'>> {}

export interface EmployeePasswordChangeRequest {
  current_password?: string;
  new_password: string;
}

export interface EmployeeRoleChangeRequest {
  role: string;
  permissions?: string[];
}

export interface EmployeeStatusChangeRequest {
  is_active: boolean;
  status: string;
}

export interface EmployeeStats {
  total_employees: number;
  active_employees: number;
  inactive_employees: number;
  employees_by_department: Record<string, number>;
  employees_by_role: Record<string, number>;
  employees_by_designation: Record<string, number>;
  recent_joinings: Employee[];
}

export interface EmployeeExistsCheck {
  email?: string;
  mobile?: string;
  pan_number?: string;
  exclude_id?: string;
}

export interface EmployeeFiles {
  pan_file?: File;
  aadhar_file?: File;
  photo?: File;
}

export interface EmployeeAttendanceSummary {
  employee_id: string;
  month: string;
  year: number;
  total_working_days: number;
  present_days: number;
  absent_days: number;
  half_days: number;
  late_arrivals: number;
  early_departures: number;
  overtime_hours: number;
}

export interface EmployeeLeaveSummary {
  employee_id: string;
  year: number;
  total_casual_leaves: number;
  used_casual_leaves: number;
  total_sick_leaves: number;
  used_sick_leaves: number;
  total_earned_leaves: number;
  used_earned_leaves: number;
  pending_leave_requests: number;
}

/**
 * Comprehensive Employee API service
 * Handles all employee-related operations
 */
class EmployeeAPI {
  private static instance: EmployeeAPI;
  private baseApi: BaseAPI;

  private constructor() {
    this.baseApi = BaseAPI.getInstance();
  }

  public static getInstance(): EmployeeAPI {
    if (!EmployeeAPI.instance) {
      EmployeeAPI.instance = new EmployeeAPI();
    }
    return EmployeeAPI.instance;
  }

  /**
   * Get list of employees with filtering and pagination
   */
  async getEmployees(filters: EmployeeFilters = {}): Promise<EmployeeListResponse> {
    try {
      const {
        skip = 0,
        limit = 10,
        include_inactive = false,
        include_deleted = false,
        organisation_id = null,
        search,
        department,
        role,
        manager_id,
        designation,
        location,
        // Date filters
        doj_from,
        doj_to,
        dol_from,
        dol_to,
        dob_from,
        dob_to
      } = filters;

      const params: Record<string, any> = {
        skip,
        limit,
        include_inactive,
        include_deleted
      };

      if (organisation_id) params.organisation_id = organisation_id;
      if (search) params.search = search;
      if (department) params.department = department;
      if (role) params.role = role;
      if (manager_id) params.manager_id = manager_id;
      if (designation) params.designation = designation;
      if (location) params.location = location;

      // Add date filters
      if (doj_from) params.date_of_joining_from = doj_from;
      if (doj_to) params.date_of_joining_to = doj_to;
      if (dol_from) params.date_of_leaving_from = dol_from;
      if (dol_to) params.date_of_leaving_to = dol_to;
      if (dob_from) params.date_of_birth_from = dob_from;
      if (dob_to) params.date_of_birth_to = dob_to;

      const response = await this.baseApi.get<EmployeeListResponse>('/api/v2/users', { params });
      return response;
    } catch (error: any) {
      console.error('Error fetching employees:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch employees');
    }
  }

  /**
   * Get employee by ID
   */
  async getEmployeeById(employeeId: string): Promise<Employee> {
    try {
      const response = await this.baseApi.get<Employee>(`/api/v2/users/${employeeId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching employee:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch employee');
    }
  }

  /**
   * Get employee by email
   */
  async getEmployeeByEmail(email: string): Promise<Employee> {
    try {
      const response = await this.baseApi.get<Employee>(`/api/v2/users/email/${email}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching employee by email:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch employee by email');
    }
  }

  /**
   * Get current employee profile
   */
  async getCurrentEmployee(): Promise<Employee> {
    try {
      const response = await this.baseApi.get<Employee>('/api/v2/users/me');
      return response;
    } catch (error: any) {
      console.error('Error fetching current employee:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch current employee');
    }
  }

  /**
   * Get employee statistics
   */
  async getEmployeeStats(): Promise<EmployeeStats> {
    try {
      const response = await this.baseApi.get<EmployeeStats>('/api/v2/users/stats');
      return response;
    } catch (error: any) {
      console.error('Error fetching employee stats:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch employee statistics');
    }
  }

  /**
   * Get direct reports for current employee
   */
  async getMyDirectReports(): Promise<Employee[]> {
    try {
      const response = await this.baseApi.get<Employee[]>('/api/v2/users/my/directs');
      return response;
    } catch (error: any) {
      console.error('Error fetching direct reports:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch direct reports');
    }
  }

  /**
   * Get direct reports for a specific manager
   */
  async getManagerDirectReports(managerId: string): Promise<Employee[]> {
    try {
      const response = await this.baseApi.get<Employee[]>('/api/v2/users/manager/directs', {
        params: { manager_id: managerId }
      });
      return response;
    } catch (error: any) {
      console.error('Error fetching manager direct reports:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch manager direct reports');
    }
  }

  /**
   * Create new employee
   */
  async createEmployee(employeeData: CreateEmployeeRequest): Promise<Employee> {
    try {
      const response = await this.baseApi.post<Employee>('/api/v2/users/create', employeeData);
      return response;
    } catch (error: any) {
      console.error('Error creating employee:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create employee');
    }
  }

  /**
   * Create employee with file uploads
   */
  async createEmployeeWithFiles(employeeData: CreateEmployeeRequest, files: EmployeeFiles = {}): Promise<Employee> {
    try {
      const formData = new FormData();
      formData.append('user_data', JSON.stringify(employeeData));

      if (files.pan_file) {
        formData.append('pan_file', files.pan_file);
      }
      if (files.aadhar_file) {
        formData.append('aadhar_file', files.aadhar_file);
      }
      if (files.photo) {
        formData.append('photo', files.photo);
      }

      const response = await this.baseApi.upload<Employee>('/api/v2/users/with-files', formData);
      return response;
    } catch (error: any) {
      console.error('Error creating employee with files:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create employee with files');
    }
  }

  /**
   * Update employee
   */
  async updateEmployee(employeeId: string, employeeData: UpdateEmployeeRequest): Promise<Employee> {
    try {
      const response = await this.baseApi.put<Employee>(`/api/v2/users/${employeeId}`, employeeData);
      return response;
    } catch (error: any) {
      console.error('Error updating employee:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update employee');
    }
  }

  /**
   * Delete employee
   */
  async deleteEmployee(employeeId: string): Promise<{ message: string }> {
    try {
      const response = await this.baseApi.delete<{ message: string }>(`/api/v2/users/${employeeId}`);
      return response;
    } catch (error: any) {
      console.error('Error deleting employee:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete employee');
    }
  }

  /**
   * Change employee password
   */
  async changeEmployeePassword(employeeId: string, passwordData: EmployeePasswordChangeRequest): Promise<{ message: string }> {
    try {
      const response = await this.baseApi.patch<{ message: string }>(`/api/v2/users/${employeeId}/password`, passwordData);
      return response;
    } catch (error: any) {
      console.error('Error changing employee password:', error);
      throw new Error(error.response?.data?.detail || 'Failed to change employee password');
    }
  }

  /**
   * Change employee role
   */
  async changeEmployeeRole(employeeId: string, roleData: EmployeeRoleChangeRequest): Promise<Employee> {
    try {
      const response = await this.baseApi.patch<Employee>(`/api/v2/users/${employeeId}/role`, roleData);
      return response;
    } catch (error: any) {
      console.error('Error changing employee role:', error);
      throw new Error(error.response?.data?.detail || 'Failed to change employee role');
    }
  }

  /**
   * Update employee status
   */
  async updateEmployeeStatus(employeeId: string, statusData: EmployeeStatusChangeRequest): Promise<Employee> {
    try {
      const response = await this.baseApi.patch<Employee>(`/api/v2/users/${employeeId}/status`, statusData);
      return response;
    } catch (error: any) {
      console.error('Error updating employee status:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update employee status');
    }
  }

  /**
   * Check if employee exists
   */
  async checkEmployeeExists(checkData: EmployeeExistsCheck): Promise<{ exists: boolean; field?: string }> {
    try {
      const response = await this.baseApi.post<{ exists: boolean; field?: string }>('/api/v2/users/check-exists', checkData);
      return response;
    } catch (error: any) {
      console.error('Error checking employee existence:', error);
      throw new Error(error.response?.data?.detail || 'Failed to check employee existence');
    }
  }

  /**
   * Search employees with advanced filters
   */
  async searchEmployees(searchQuery: string, filters: Omit<EmployeeFilters, 'search'> = {}): Promise<EmployeeListResponse> {
    try {
      const searchFilters = { ...filters, search: searchQuery };
      return await this.getEmployees(searchFilters);
    } catch (error: any) {
      console.error('Error searching employees:', error);
      throw new Error(error.response?.data?.detail || 'Failed to search employees');
    }
  }

  /**
   * Get employee attendance summary
   */
  async getEmployeeAttendanceSummary(employeeId: string, month: number, year: number): Promise<EmployeeAttendanceSummary> {
    try {
      const response = await this.baseApi.get<EmployeeAttendanceSummary>(`/api/v2/users/${employeeId}/attendance/summary`, {
        params: { month, year }
      });
      return response;
    } catch (error: any) {
      console.error('Error fetching employee attendance summary:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch employee attendance summary');
    }
  }

  /**
   * Get employee leave summary
   */
  async getEmployeeLeaveSummary(employeeId: string, year: number): Promise<EmployeeLeaveSummary> {
    try {
      const response = await this.baseApi.get<EmployeeLeaveSummary>(`/api/v2/users/${employeeId}/leaves/summary`, {
        params: { year }
      });
      return response;
    } catch (error: any) {
      console.error('Error fetching employee leave summary:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch employee leave summary');
    }
  }

  /**
   * Import employees from file
   */
  async importEmployees(file: File): Promise<{ message: string; imported_count: number; errors?: any[] }> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.baseApi.upload<{ message: string; imported_count: number; errors?: any[] }>(
        '/api/v2/users/import',
        formData
      );
      return response;
    } catch (error: any) {
      console.error('Error importing employees:', error);
      throw new Error(error.response?.data?.detail || 'Failed to import employees');
    }
  }

  /**
   * Export employees to file
   */
  async exportEmployees(filters: EmployeeFilters = {}): Promise<Blob> {
    try {
      const response = await this.baseApi.download('/api/v2/users/export', {
        params: filters
      });
      return response;
    } catch (error: any) {
      console.error('Error exporting employees:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export employees');
    }
  }

  /**
   * Get employee departments
   */
  async getEmployeeDepartments(): Promise<{ departments: string[] }> {
    try {
      const response = await this.baseApi.get<{ departments: string[] }>('/api/v2/users/departments');
      return response;
    } catch (error: any) {
      console.error('Error fetching employee departments:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch employee departments');
    }
  }

  /**
   * Get employee designations
   */
  async getEmployeeDesignations(): Promise<{ designations: string[] }> {
    try {
      const response = await this.baseApi.get<{ designations: string[] }>('/api/v2/users/designations');
      return response;
    } catch (error: any) {
      console.error('Error fetching employee designations:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch employee designations');
    }
  }
}

// Export singleton instance
export const employeeApi = EmployeeAPI.getInstance();
export default employeeApi; 