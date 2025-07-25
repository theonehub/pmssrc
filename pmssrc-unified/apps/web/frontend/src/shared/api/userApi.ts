import { BaseAPI } from './baseApi';

// Type definitions for User Management
export interface PersonalDetails {
  gender: string;
  date_of_birth: string;
  date_of_joining: string;
  mobile: string;
  pan_number?: string;
  aadhar_number?: string;
  uan_number?: string;
  esi_number?: string;
  formatted_mobile?: string;
  masked_pan?: string;
  masked_aadhar?: string;
}

export interface User {
  employee_id: string;
  name: string;
  email: string;
  role: string;
  personal_details?: PersonalDetails;
  department?: string;
  designation?: string;
  manager_id?: string;
  location?: string;
  created_at?: string;
  updated_at?: string;
  is_active: boolean;
  status: string;
  profile_picture_url?: string;
  pan_document_path?: string;
  aadhar_document_path?: string;
  photo_path?: string;
  // Bank Details
  bank_details?: {
    account_number: string;
    bank_name: string;
    ifsc_code: string;
    account_holder_name: string;
    branch_name?: string;
    account_type?: string;
  };
  permissions?: {
    role?: string;
  };
}

export interface UserFilters {
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
}

export interface UserListResponse {
  total: number;
  users: User[];
  skip: number;
  limit: number;
}

export interface CreateUserRequest extends Omit<User, 'created_at' | 'updated_at' | 'employee_id'> {
  password: string;
}

export interface UpdateUserRequest extends Partial<Omit<User, 'employee_id' | 'created_at' | 'updated_at'>> {}

export interface PasswordChangeRequest {
  current_password?: string;
  new_password: string;
}

export interface RoleChangeRequest {
  role: string;
  permissions?: string[];
}

export interface StatusChangeRequest {
  status: string;
}

export interface UserStats {
  total_users: number;
  active_users: number;
  inactive_users: number;
  users_by_department: Record<string, number>;
  users_by_role: Record<string, number>;
  users_by_designation: Record<string, number>;
  recent_joinings: User[];
}

export interface UserExistsCheck {
  email?: string;
  mobile?: string;
  pan_number?: string;
  exclude_id?: string;
}

export interface UserFiles {
  pan_file?: File;
  aadhar_file?: File;
  photo?: File;
}

export interface ImportOptions {
  update_existing?: boolean;
  skip_errors?: boolean;
}

export interface ImportResult {
  success: boolean;
  message: string;
  imported_count?: number;
  errors?: string[];
}

/**
 * Enhanced User Management API using BaseAPI pattern
 * Provides comprehensive user management functionality
 */
export class UserAPI {
  private baseApi: BaseAPI;

  constructor() {
    this.baseApi = BaseAPI.getInstance();
  }

  /**
   * Get all users with pagination and filters
   */
  async getUsers(filters: UserFilters = {}): Promise<UserListResponse> {
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
        location
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

      const response = await this.baseApi.get<UserListResponse>('/v2/users', { params });
      return response;
    } catch (error: any) {
      console.error('Error fetching users:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch users');
    }
  }

  /**
   * Get user by ID
   */
  async getUserById(userId: string): Promise<User> {
    try {
      const response = await this.baseApi.get<User>(`/v2/users/${userId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching user:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch user');
    }
  }

  /**
   * Get user by email
   */
  async getUserByEmail(email: string): Promise<User> {
    try {
      const response = await this.baseApi.get<User>(`/v2/users/email/${email}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching user by email:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch user by email');
    }
  }

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await this.baseApi.get<User>('/v2/users/me');
      return response;
    } catch (error: any) {
      console.error('Error fetching current user:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch current user');
    }
  }

  /**
   * Get user statistics
   */
  async getUserStats(): Promise<UserStats> {
    try {
      const response = await this.baseApi.get<UserStats>('/v2/users/stats');
      return response;
    } catch (error: any) {
      console.error('Error fetching user stats:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch user statistics');
    }
  }

  /**
   * Get direct reports for current user
   */
  async getDirectReports(): Promise<User[]> {
    try {
      const response = await this.baseApi.get<User[]>('/v2/users/my/directs');
      return response;
    } catch (error: any) {
      console.error('Error fetching direct reports:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch direct reports');
    }
  }

  /**
   * Get direct reports for a specific manager
   */
  async getManagerDirectReports(managerId: string): Promise<User[]> {
    try {
      const response = await this.baseApi.get<User[]>('/v2/users/manager/directs', {
        params: { manager_id: managerId }
      });
      return response;
    } catch (error: any) {
      console.error('Error fetching manager direct reports:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch manager direct reports');
    }
  }

  /**
   * Create a new user
   */
  async createUser(userData: CreateUserRequest): Promise<User> {
    try {
      const response = await this.baseApi.post<User>('/v2/users/create', userData);
      return response;
    } catch (error: any) {
      console.error('Error creating user:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create user');
    }
  }

  /**
   * Create user with file upload
   */
  async createUserWithFiles(userData: CreateUserRequest, files: UserFiles): Promise<User> {
    try {
      const formData = new FormData();
      // Add user data as JSON string
      formData.append('user_data', JSON.stringify(userData));
      // Add files with correct field names
      if (files?.pan_file) formData.append('pan_file', files.pan_file);
      if (files?.aadhar_file) formData.append('aadhar_file', files.aadhar_file);
      if (files?.photo) formData.append('photo', files.photo);
      // Use the correct endpoint
      const response = await this.baseApi.upload<User>('/v2/users/create-with-files', formData);
      return response;
    } catch (error: any) {
      console.error('Error creating user with files:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create user with files');
    }
  }

  /**
   * Update user
   */
  async updateUser(userId: string, userData: UpdateUserRequest): Promise<User> {
    try {
      const response = await this.baseApi.put<User>(`/v2/users/${userId}`, userData);
      return response;
    } catch (error: any) {
      console.error('Error updating user:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update user');
    }
  }

  /**
   * Update user with file upload
   */
  async updateUserWithFiles(userId: string, userData: UpdateUserRequest, files: File[]): Promise<User> {
    try {
      const formData = new FormData();
      
      // Add user data
      formData.append('user_data', JSON.stringify(userData));
      
      // Add files
      files.forEach((file, index) => {
        formData.append(`file_${index}`, file);
      });

      const response = await this.baseApi.upload<User>(`/v2/users/${userId}/with-files`, formData);
      return response;
    } catch (error: any) {
      console.error('Error updating user with files:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update user with files');
    }
  }

  /**
   * Delete user
   */
  async deleteUser(userId: string): Promise<void> {
    try {
      await this.baseApi.delete(`/v2/users/${userId}`);
    } catch (error: any) {
      console.error('Error deleting user:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete user');
    }
  }

  /**
   * Change user password
   */
  async changeUserPassword(userId: string, passwordData: PasswordChangeRequest): Promise<{ message: string }> {
    try {
      const response = await this.baseApi.patch<{ message: string }>(`/v2/users/${userId}/password`, passwordData);
      return response;
    } catch (error: any) {
      console.error('Error changing user password:', error);
      throw new Error(error.response?.data?.detail || 'Failed to change user password');
    }
  }

  /**
   * Change user role
   */
  async changeUserRole(userId: string, roleData: RoleChangeRequest): Promise<User> {
    try {
      const response = await this.baseApi.patch<User>(`/v2/users/${userId}/role`, roleData);
      return response;
    } catch (error: any) {
      console.error('Error changing user role:', error);
      throw new Error(error.response?.data?.detail || 'Failed to change user role');
    }
  }

  /**
   * Update user status
   */
  async updateUserStatus(userId: string, statusData: StatusChangeRequest): Promise<User> {
    try {
      const response = await this.baseApi.patch<User>(`/v2/users/${userId}/status`, statusData);
      return response;
    } catch (error: any) {
      console.error('Error updating user status:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update user status');
    }
  }

  /**
   * Check if user exists
   */
  async checkUserExists(checkData: { field: string; value: string; exclude_id?: string }): Promise<{ exists: boolean; field?: string }> {
    try {
      const response = await this.baseApi.post<{ exists: boolean; field?: string }>('/v2/users/check-exists', checkData);
      return response;
    } catch (error: any) {
      console.error('Error checking user exists:', error);
      throw new Error(error.response?.data?.detail || 'Failed to check if user exists');
    }
  }

  /**
   * Search users with advanced filters
   */
  async searchUsers(searchQuery: string, filters: Omit<UserFilters, 'search'> = {}): Promise<UserListResponse> {
    try {
      const searchFilters = { ...filters, search: searchQuery };
      return await this.getUsers(searchFilters);
    } catch (error: any) {
      console.error('Error searching users:', error);
      throw new Error(error.response?.data?.detail || 'Failed to search users');
    }
  }

  /**
   * Bulk import users
   */
  async importUsers(file: File, options: ImportOptions = {}): Promise<ImportResult> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (options.update_existing !== undefined) {
        formData.append('update_existing', options.update_existing.toString());
      }
      if (options.skip_errors !== undefined) {
        formData.append('skip_errors', options.skip_errors.toString());
      }

      const response = await this.baseApi.upload<ImportResult>(
        '/v2/users/import',
        formData
      );
      return response;
    } catch (error: any) {
      console.error('Error importing users:', error);
      throw new Error(error.response?.data?.detail || 'Failed to import users');
    }
  }

  /**
   * Export users
   */
  async exportUsers(filters: UserFilters = {}): Promise<Blob> {
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
        location
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

      const response = await this.baseApi.download('/v2/users/export', {
        params
      });
      return response;
    } catch (error: any) {
      console.error('Error exporting users:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export users');
    }
  }

  /**
   * Download user import template
   */
  async downloadTemplate(): Promise<Blob> {
    try {
      const response = await this.baseApi.download('/v2/users/template');
      return response;
    } catch (error: any) {
      console.error('Error downloading template:', error);
      throw new Error(error.response?.data?.detail || 'Failed to download template');
    }
  }

  /**
   * Get all departments
   */
  async getDepartments(): Promise<string[]> {
    try {
      const response = await this.baseApi.get<{ departments: string[] }>('/v2/users/departments');
      return response.departments;
    } catch (error: any) {
      console.error('Error fetching departments:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch departments');
    }
  }

  /**
   * Get all designations
   */
  async getDesignations(): Promise<string[]> {
    try {
      const response = await this.baseApi.get<{ designations: string[] }>('/v2/users/designations');
      return response.designations;
    } catch (error: any) {
      console.error('Error fetching designations:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch designations');
    }
  }

  /**
   * Upload user profile picture
   */
  async uploadProfilePicture(userId: string, photoFile: File): Promise<{ profile_picture_url: string }> {
    try {
      const formData = new FormData();
      formData.append('photo', photoFile);

      const response = await this.baseApi.upload<{ profile_picture_url: string }>(
        `/v2/users/${userId}/profile-picture`,
        formData
      );
      return response;
    } catch (error: any) {
      console.error('Error uploading profile picture:', error);
      throw new Error(error.response?.data?.detail || 'Failed to upload profile picture');
    }
  }

  /**
   * Upload user documents
   */
  async uploadUserDocuments(userId: string, documents: { pan_file?: File; aadhar_file?: File }): Promise<{
    pan_document_path?: string;
    aadhar_document_path?: string;
  }> {
    try {
      const formData = new FormData();
      
      if (documents.pan_file) {
        formData.append('pan_file', documents.pan_file);
      }
      if (documents.aadhar_file) {
        formData.append('aadhar_file', documents.aadhar_file);
      }

      const response = await this.baseApi.upload<{
        pan_document_path?: string;
        aadhar_document_path?: string;
      }>(`/v2/users/${userId}/documents`, formData);
      return response;
    } catch (error: any) {
      console.error('Error uploading user documents:', error);
      throw new Error(error.response?.data?.detail || 'Failed to upload user documents');
    }
  }

  // Add missing methods for legacy compatibility
  async getUserByEmpIdLegacy(empId: string): Promise<User> {
    const response = await this.baseApi.get(`/v2/users/${empId}`);
    return response.data;
  }

  async updateUserLegacy(empId: string, userData: Partial<User>): Promise<User> {
    const response = await this.baseApi.put(`/v2/users/${empId}`, userData);
    return response.data;
  }
}

// Export singleton instance
export const userApi = new UserAPI();
export default userApi; 