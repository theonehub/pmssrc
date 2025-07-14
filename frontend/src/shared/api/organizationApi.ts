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
   * Get current organization (based on authenticated user)
   */
  async getCurrentOrganization(): Promise<Organization> {
    try {
      const response = await this.baseApi.get<Organization>('/api/v2/organisations/current/organisation');
      return response;
    } catch (error: any) {
      console.error('Error fetching current organization:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch current organization');
    }
  }
}

// Export singleton instance
export const organizationApi = OrganizationAPI.getInstance();
export default organizationApi; 