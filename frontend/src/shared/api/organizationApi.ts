import { BaseAPI } from './baseApi';

// Type definitions for Organization API
export interface Organization {
  org_id: string;
  hostname: string;
  company_name: string;
  admin_email: string;
  admin_name: string;
  admin_mobile?: string;
  industry?: string;
  company_size?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  website?: string;
  logo_url?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  subscription_plan?: string;
  features: string[];
  settings: OrganizationSettings;
}

export interface OrganizationSettings {
  working_hours: {
    start_time: string;
    end_time: string;
    days: string[];
  };
  leave_policy: {
    casual_leaves: number;
    sick_leaves: number;
    earned_leaves: number;
    carry_forward: boolean;
  };
  attendance_settings: {
    grace_period_minutes: number;
    half_day_hours: number;
    full_day_hours: number;
    overtime_enabled: boolean;
  };
  payroll_settings: {
    pay_frequency: 'monthly' | 'bi-weekly' | 'weekly';
    currency: string;
    tax_calculation_enabled: boolean;
  };
  notification_settings: {
    email_notifications: boolean;
    sms_notifications: boolean;
    leave_approval_notifications: boolean;
    attendance_alerts: boolean;
  };
}

export interface OrganizationFilters {
  skip?: number;
  limit?: number;
  search?: string;
  industry?: string;
  company_size?: string;
  is_active?: boolean;
  subscription_plan?: string;
}

export interface OrganizationListResponse {
  total: number;
  organizations: Organization[];
  skip: number;
  limit: number;
}

export interface CreateOrganizationRequest {
  hostname: string;
  company_name: string;
  admin_email: string;
  admin_name: string;
  admin_mobile?: string;
  industry?: string;
  company_size?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  website?: string;
  subscription_plan?: string;
}

export interface UpdateOrganizationRequest {
  company_name?: string;
  admin_email?: string;
  admin_name?: string;
  admin_mobile?: string;
  industry?: string;
  company_size?: string;
  address?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
  website?: string;
  subscription_plan?: string;
  is_active?: boolean;
  settings?: Partial<OrganizationSettings>;
}

export interface OrganizationStats {
  total_employees: number;
  active_employees: number;
  departments: string[];
  recent_activities: Array<{
    type: string;
    description: string;
    timestamp: string;
  }>;
  subscription_info: {
    plan: string;
    expires_at: string;
    features: string[];
  };
}

/**
 * Comprehensive Organization API service
 * Handles all organization-related operations
 */
class OrganizationAPI {
  private static instance: OrganizationAPI;
  private baseApi: BaseAPI;

  private constructor() {
    this.baseApi = BaseAPI.getInstance();
  }

  public static getInstance(): OrganizationAPI {
    if (!OrganizationAPI.instance) {
      OrganizationAPI.instance = new OrganizationAPI();
    }
    return OrganizationAPI.instance;
  }

  /**
   * Get list of organizations with filtering and pagination
   */
  async getOrganizations(filters: OrganizationFilters = {}): Promise<OrganizationListResponse> {
    try {
      const {
        skip = 0,
        limit = 10,
        search,
        industry,
        company_size,
        is_active,
        subscription_plan
      } = filters;

      const params: Record<string, any> = {
        skip,
        limit
      };

      if (search) params.search = search;
      if (industry) params.industry = industry;
      if (company_size) params.company_size = company_size;
      if (is_active !== undefined) params.is_active = is_active;
      if (subscription_plan) params.subscription_plan = subscription_plan;

      const response = await this.baseApi.get<OrganizationListResponse>('/api/v2/organizations', { params });
      return response;
    } catch (error: any) {
      console.error('Error fetching organizations:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch organizations');
    }
  }

  /**
   * Get organization by ID
   */
  async getOrganizationById(orgId: string): Promise<Organization> {
    try {
      const response = await this.baseApi.get<Organization>(`/api/v2/organizations/${orgId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching organization:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch organization');
    }
  }

  /**
   * Get organization by hostname
   */
  async getOrganizationByHostname(hostname: string): Promise<Organization> {
    try {
      const response = await this.baseApi.get<Organization>(`/api/v2/organizations/hostname/${hostname}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching organization by hostname:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch organization by hostname');
    }
  }

  /**
   * Get current organization (based on authenticated user)
   */
  async getCurrentOrganization(): Promise<Organization> {
    try {
      const response = await this.baseApi.get<Organization>('/api/v2/organizations/current');
      return response;
    } catch (error: any) {
      console.error('Error fetching current organization:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch current organization');
    }
  }

  /**
   * Create new organization
   */
  async createOrganization(orgData: CreateOrganizationRequest): Promise<Organization> {
    try {
      const response = await this.baseApi.post<Organization>('/api/v2/organizations', orgData);
      return response;
    } catch (error: any) {
      console.error('Error creating organization:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create organization');
    }
  }

  /**
   * Update organization
   */
  async updateOrganization(orgId: string, orgData: UpdateOrganizationRequest): Promise<Organization> {
    try {
      const response = await this.baseApi.put<Organization>(`/api/v2/organizations/${orgId}`, orgData);
      return response;
    } catch (error: any) {
      console.error('Error updating organization:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update organization');
    }
  }

  /**
   * Update organization settings
   */
  async updateOrganizationSettings(orgId: string, settings: Partial<OrganizationSettings>): Promise<Organization> {
    try {
      const response = await this.baseApi.patch<Organization>(`/api/v2/organizations/${orgId}/settings`, settings);
      return response;
    } catch (error: any) {
      console.error('Error updating organization settings:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update organization settings');
    }
  }

  /**
   * Delete organization
   */
  async deleteOrganization(orgId: string): Promise<{ message: string }> {
    try {
      const response = await this.baseApi.delete<{ message: string }>(`/api/v2/organizations/${orgId}`);
      return response;
    } catch (error: any) {
      console.error('Error deleting organization:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete organization');
    }
  }

  /**
   * Activate/Deactivate organization
   */
  async toggleOrganizationStatus(orgId: string, isActive: boolean): Promise<Organization> {
    try {
      const response = await this.baseApi.patch<Organization>(`/api/v2/organizations/${orgId}/status`, {
        is_active: isActive
      });
      return response;
    } catch (error: any) {
      console.error('Error toggling organization status:', error);
      throw new Error(error.response?.data?.detail || 'Failed to toggle organization status');
    }
  }

  /**
   * Get organization statistics
   */
  async getOrganizationStats(orgId: string): Promise<OrganizationStats> {
    try {
      const response = await this.baseApi.get<OrganizationStats>(`/api/v2/organizations/${orgId}/stats`);
      return response;
    } catch (error: any) {
      console.error('Error fetching organization stats:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch organization statistics');
    }
  }

  /**
   * Upload organization logo
   */
  async uploadOrganizationLogo(orgId: string, logoFile: File): Promise<{ logo_url: string }> {
    try {
      const formData = new FormData();
      formData.append('logo', logoFile);

      const response = await this.baseApi.upload<{ logo_url: string }>(
        `/api/v2/organizations/${orgId}/logo`,
        formData
      );
      return response;
    } catch (error: any) {
      console.error('Error uploading organization logo:', error);
      throw new Error(error.response?.data?.detail || 'Failed to upload organization logo');
    }
  }

  /**
   * Check if hostname is available
   */
  async checkHostnameAvailability(hostname: string): Promise<{ available: boolean }> {
    try {
      const response = await this.baseApi.get<{ available: boolean }>('/api/v2/organizations/check-hostname', {
        params: { hostname }
      });
      return response;
    } catch (error: any) {
      console.error('Error checking hostname availability:', error);
      throw new Error(error.response?.data?.detail || 'Failed to check hostname availability');
    }
  }

  /**
   * Get organization features
   */
  async getOrganizationFeatures(orgId: string): Promise<{ features: string[] }> {
    try {
      const response = await this.baseApi.get<{ features: string[] }>(`/api/v2/organizations/${orgId}/features`);
      return response;
    } catch (error: any) {
      console.error('Error fetching organization features:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch organization features');
    }
  }

  /**
   * Update organization features
   */
  async updateOrganizationFeatures(orgId: string, features: string[]): Promise<{ message: string }> {
    try {
      const response = await this.baseApi.patch<{ message: string }>(`/api/v2/organizations/${orgId}/features`, {
        features
      });
      return response;
    } catch (error: any) {
      console.error('Error updating organization features:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update organization features');
    }
  }

  /**
   * Get subscription information
   */
  async getSubscriptionInfo(orgId: string): Promise<{
    plan: string;
    status: string;
    expires_at: string;
    features: string[];
    limits: Record<string, number>;
  }> {
    try {
      const response = await this.baseApi.get(`/api/v2/organizations/${orgId}/subscription`);
      return response;
    } catch (error: any) {
      console.error('Error fetching subscription info:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch subscription information');
    }
  }

  /**
   * Export organization data
   */
  async exportOrganizationData(orgId: string, format: 'pdf' | 'excel'): Promise<Blob> {
    try {
      const response = await this.baseApi.download(`/api/v2/organizations/${orgId}/export`, {
        params: { format }
      });
      return response;
    } catch (error: any) {
      console.error('Error exporting organization data:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export organization data');
    }
  }
}

// Export singleton instance
export const organizationApi = OrganizationAPI.getInstance();
export default organizationApi; 