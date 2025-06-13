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
   * Get list of leave requests with filtering and pagination
   */
  async getLeaveRequests(filters: LeaveFilters = {}): Promise<LeaveListResponse> {
    try {
      const {
        skip = 0,
        limit = 10,
        employee_id,
        leave_type,
        status,
        start_date,
        end_date,
        applied_date_from,
        applied_date_to,
        search,
        manager_id,
        department
      } = filters;

      const params: Record<string, any> = {
        skip,
        limit
      };

      if (employee_id) params.employee_id = employee_id;
      if (leave_type) params.leave_type = leave_type;
      if (status) params.status = status;
      if (start_date) params.start_date = start_date;
      if (end_date) params.end_date = end_date;
      if (applied_date_from) params.applied_date_from = applied_date_from;
      if (applied_date_to) params.applied_date_to = applied_date_to;
      if (search) params.search = search;
      if (manager_id) params.manager_id = manager_id;
      if (department) params.department = department;

      const response = await this.baseApi.get<LeaveListResponse>('/api/v2/leaves', { params });
      return response;
    } catch (error: any) {
      console.error('Error fetching leave requests:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch leave requests');
    }
  }

  /**
   * Get leave request by ID
   */
  async getLeaveRequestById(leaveId: string): Promise<LeaveRequest> {
    try {
      const response = await this.baseApi.get<LeaveRequest>(`/api/v2/leaves/${leaveId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching leave request:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch leave request');
    }
  }

  /**
   * Get employee leave balance
   */
  async getEmployeeLeaveBalance(employeeId: string): Promise<LeaveBalance> {
    try {
      const response = await this.baseApi.get<LeaveBalance>(`/api/v2/leaves/balance/${employeeId}`);
      return response;
    } catch (error: any) {
      console.error('Error fetching leave balance:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch leave balance');
    }
  }

  /**
   * Get current user's leave balance
   */
  async getMyLeaveBalance(): Promise<LeaveBalance> {
    try {
      const response = await this.baseApi.get<LeaveBalance>('/api/v2/leaves/my-balance');
      return response;
    } catch (error: any) {
      console.error('Error fetching my leave balance:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch leave balance');
    }
  }

  /**
   * Create new leave request
   */
  async createLeaveRequest(leaveData: CreateLeaveRequest): Promise<LeaveRequest> {
    try {
      const response = await this.baseApi.post<LeaveRequest>('/api/v2/leaves', leaveData);
      return response;
    } catch (error: any) {
      console.error('Error creating leave request:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create leave request');
    }
  }

  /**
   * Create leave request with documents
   */
  async createLeaveRequestWithDocuments(leaveData: CreateLeaveRequest, documents: File[]): Promise<LeaveRequest> {
    try {
      const formData = new FormData();
      formData.append('leave_data', JSON.stringify(leaveData));

      documents.forEach((file) => {
        formData.append(`documents`, file);
      });

      const response = await this.baseApi.upload<LeaveRequest>('/api/v2/leaves/with-documents', formData);
      return response;
    } catch (error: any) {
      console.error('Error creating leave request with documents:', error);
      throw new Error(error.response?.data?.detail || 'Failed to create leave request with documents');
    }
  }

  /**
   * Update leave request
   */
  async updateLeaveRequest(leaveId: string, leaveData: UpdateLeaveRequest): Promise<LeaveRequest> {
    try {
      const response = await this.baseApi.put<LeaveRequest>(`/api/v2/leaves/${leaveId}`, leaveData);
      return response;
    } catch (error: any) {
      console.error('Error updating leave request:', error);
      throw new Error(error.response?.data?.detail || 'Failed to update leave request');
    }
  }

  /**
   * Cancel leave request
   */
  async cancelLeaveRequest(leaveId: string, reason?: string): Promise<LeaveRequest> {
    try {
      const response = await this.baseApi.patch<LeaveRequest>(`/api/v2/leaves/${leaveId}/cancel`, {
        reason
      });
      return response;
    } catch (error: any) {
      console.error('Error cancelling leave request:', error);
      throw new Error(error.response?.data?.detail || 'Failed to cancel leave request');
    }
  }

  /**
   * Approve or reject leave request
   */
  async processLeaveRequest(leaveId: string, approvalData: LeaveApprovalRequest): Promise<LeaveRequest> {
    try {
      const response = await this.baseApi.patch<LeaveRequest>(`/api/v2/leaves/${leaveId}/process`, approvalData);
      return response;
    } catch (error: any) {
      console.error('Error processing leave request:', error);
      throw new Error(error.response?.data?.detail || 'Failed to process leave request');
    }
  }

  /**
   * Get pending leave requests for approval
   */
  async getPendingLeaveRequests(): Promise<LeaveRequest[]> {
    try {
      const response = await this.baseApi.get<LeaveRequest[]>('/api/v2/leaves/pending-approvals');
      return response;
    } catch (error: any) {
      console.error('Error fetching pending leave requests:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch pending leave requests');
    }
  }

  /**
   * Get leave types
   */
  async getLeaveTypes(): Promise<LeaveType[]> {
    try {
      const response = await this.baseApi.get<LeaveType[]>('/api/v2/leaves/types');
      return response;
    } catch (error: any) {
      console.error('Error fetching leave types:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch leave types');
    }
  }

  /**
   * Get leave statistics
   */
  async getLeaveStats(startDate?: string, endDate?: string): Promise<LeaveStats> {
    try {
      const params: Record<string, any> = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const response = await this.baseApi.get<LeaveStats>('/api/v2/leaves/stats', { params });
      return response;
    } catch (error: any) {
      console.error('Error fetching leave statistics:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch leave statistics');
    }
  }

  /**
   * Get leave calendar for a specific month
   */
  async getLeaveCalendar(year: number, month: number): Promise<LeaveCalendar[]> {
    try {
      const response = await this.baseApi.get<LeaveCalendar[]>('/api/v2/leaves/calendar', {
        params: { year, month }
      });
      return response;
    } catch (error: any) {
      console.error('Error fetching leave calendar:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch leave calendar');
    }
  }

  /**
   * Get team leave calendar
   */
  async getTeamLeaveCalendar(year: number, month: number, managerId?: string): Promise<LeaveCalendar[]> {
    try {
      const params: Record<string, any> = { year, month };
      if (managerId) params.manager_id = managerId;

      const response = await this.baseApi.get<LeaveCalendar[]>('/api/v2/leaves/team-calendar', { params });
      return response;
    } catch (error: any) {
      console.error('Error fetching team leave calendar:', error);
      throw new Error(error.response?.data?.detail || 'Failed to fetch team leave calendar');
    }
  }

  /**
   * Check leave eligibility
   */
  async checkLeaveEligibility(
    employeeId: string,
    leaveType: string,
    startDate: string,
    endDate: string
  ): Promise<{
    eligible: boolean;
    message: string;
    conflicts?: Array<{
      date: string;
      reason: string;
    }>;
  }> {
    try {
      const response = await this.baseApi.post('/api/v2/leaves/check-eligibility', {
        employee_id: employeeId,
        leave_type: leaveType,
        start_date: startDate,
        end_date: endDate
      });
      return response;
    } catch (error: any) {
      console.error('Error checking leave eligibility:', error);
      throw new Error(error.response?.data?.detail || 'Failed to check leave eligibility');
    }
  }

  /**
   * Export leave reports
   */
  async exportLeaveReports(
    format: 'pdf' | 'excel',
    filters: LeaveFilters = {}
  ): Promise<Blob> {
    try {
      const params = { ...filters, format };
      const response = await this.baseApi.download('/api/v2/leaves/export', { params });
      return response;
    } catch (error: any) {
      console.error('Error exporting leave reports:', error);
      throw new Error(error.response?.data?.detail || 'Failed to export leave reports');
    }
  }

  /**
   * Import leave data from file
   */
  async importLeaveData(file: File): Promise<{ message: string; imported_count: number; errors?: any[] }> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.baseApi.upload<{ message: string; imported_count: number; errors?: any[] }>(
        '/api/v2/leaves/import',
        formData
      );
      return response;
    } catch (error: any) {
      console.error('Error importing leave data:', error);
      throw new Error(error.response?.data?.detail || 'Failed to import leave data');
    }
  }

  /**
   * Send leave reminder notifications
   */
  async sendLeaveReminders(): Promise<{ message: string; sent_count: number }> {
    try {
      const response = await this.baseApi.post<{ message: string; sent_count: number }>('/api/v2/leaves/send-reminders');
      return response;
    } catch (error: any) {
      console.error('Error sending leave reminders:', error);
      throw new Error(error.response?.data?.detail || 'Failed to send leave reminders');
    }
  }
}

// Export singleton instance
export const leavesApi = LeavesAPI.getInstance();
export default leavesApi; 