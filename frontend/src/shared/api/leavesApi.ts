import { BaseAPI } from './baseApi';

// Type definitions for Leaves API
export interface LeaveRequest {
  leave_id: string;
  employee_id: string;
  employee_name?: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  number_of_days: number;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  applied_date: string;
  approved_by?: string;
  approved_date?: string;
  rejection_reason?: string;
  is_half_day: boolean;
  half_day_session?: 'first_half' | 'second_half';
  emergency_contact?: string;
  documents?: string[];
  created_at: string;
  updated_at: string;
}

export interface LeaveBalance {
  employee_id: string;
  casual_leaves: number;
  sick_leaves: number;
  earned_leaves: number;
  total_leaves: number;
  used_casual_leaves: number;
  used_sick_leaves: number;
  used_earned_leaves: number;
  remaining_casual_leaves: number;
  remaining_sick_leaves: number;
  remaining_earned_leaves: number;
  carry_forward_leaves: number;
}

export interface LeaveType {
  leave_type_id: string;
  name: string;
  code: string;
  description?: string;
  max_days_per_year: number;
  max_consecutive_days: number;
  is_carry_forward: boolean;
  requires_approval: boolean;
  is_active: boolean;
  gender_specific?: 'male' | 'female' | null;
  min_notice_days: number;
  max_advance_days: number;
}

export interface LeaveFilters {
  skip?: number;
  limit?: number;
  employee_id?: string;
  leave_type?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  applied_date_from?: string;
  applied_date_to?: string;
  search?: string;
  manager_id?: string;
  department?: string;
}

export interface LeaveListResponse {
  total: number;
  leaves: LeaveRequest[];
  skip: number;
  limit: number;
}

export interface CreateLeaveRequest {
  employee_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string;
  is_half_day: boolean;
  half_day_session?: 'first_half' | 'second_half';
  emergency_contact?: string;
}

export interface UpdateLeaveRequest {
  leave_type?: string;
  start_date?: string;
  end_date?: string;
  reason?: string;
  is_half_day?: boolean;
  half_day_session?: 'first_half' | 'second_half';
  emergency_contact?: string;
}

export interface LeaveApprovalRequest {
  status: 'approved' | 'rejected';
  rejection_reason?: string;
  comments?: string;
}

export interface LeaveStats {
  total_requests: number;
  pending_requests: number;
  approved_requests: number;
  rejected_requests: number;
  leave_distribution: {
    leave_type: string;
    count: number;
    percentage: number;
  }[];
  monthly_breakdown: {
    month: string;
    total_leaves: number;
    approved_leaves: number;
  }[];
  top_reasons: {
    reason: string;
    count: number;
  }[];
}

export interface LeaveCalendar {
  date: string;
  leaves: Array<{
    employee_id: string;
    employee_name: string;
    leave_type: string;
    is_half_day: boolean;
    half_day_session?: string;
  }>;
  public_holiday?: {
    name: string;
    description?: string;
  };
  is_weekend: boolean;
}

/**
 * Comprehensive Leaves API service
 * Handles all leave-related operations
 */
class LeavesAPI {
  private static instance: LeavesAPI;
  private baseApi: BaseAPI;

  private constructor() {
    this.baseApi = BaseAPI.getInstance();
  }

  public static getInstance(): LeavesAPI {
    if (!LeavesAPI.instance) {
      LeavesAPI.instance = new LeavesAPI();
    }
    return LeavesAPI.instance;
  }

  /**
   * Approve or reject leave request
   */
  async processLeaveRequest(leaveId: string, approvalData: LeaveApprovalRequest): Promise<LeaveRequest> {
    try {
      const params = {
        status: approvalData.status,
        comments: approvalData.comments || approvalData.rejection_reason
      };
      const response = await this.baseApi.put<LeaveRequest>(`/api/v2/leaves/${leaveId}/status`, {}, { params });
      return response;
    } catch (error: any) {
      console.error('Error processing leave request:', error);
      throw new Error(error.response?.data?.detail || 'Failed to process leave request');
    }
  }
}

// Export singleton instance
export const leavesApi = LeavesAPI.getInstance();
export default leavesApi; 