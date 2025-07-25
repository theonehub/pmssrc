import { apiClient } from '@pmssrc/api-client';
import { LeaveRequest, LeaveRecord, LeaveType } from '@pmssrc/shared-types';
import { NetworkService } from '../../../shared/utils/NetworkService';

export interface LeaveApplicationData {
  leaveType: LeaveType;
  startDate: string;
  endDate: string;
  reason: string;
  halfDay?: boolean;
  halfDayType?: 'morning' | 'afternoon';
}

export interface LeaveBalance {
  totalLeaves: number;
  usedLeaves: number;
  availableLeaves: number;
  leaveType: LeaveType;
}

export class LeaveService {
  /**
   * Apply for leave
   */
  static async applyLeave(userId: string, leaveData: LeaveApplicationData): Promise<LeaveRecord> {
    return NetworkService.withInternetCheck(() =>
      apiClient.applyLeave({
        userId,
        leaveType: leaveData.leaveType,
        startDate: leaveData.startDate,
        endDate: leaveData.endDate,
        reason: leaveData.reason,
        halfDay: leaveData.halfDay || false,
        halfDayType: leaveData.halfDayType,
      })
    );
  }

  /**
   * Get user's leave history
   */
  static async getLeaveHistory(userId: string, startDate?: string, endDate?: string): Promise<LeaveRecord[]> {
    return NetworkService.withInternetCheck(() =>
      apiClient.getLeaveHistory(userId, startDate, endDate)
    );
  }

  /**
   * Get leave balance for user
   */
  static async getLeaveBalance(userId: string): Promise<LeaveBalance[]> {
    return NetworkService.withInternetCheck(() =>
      apiClient.getLeaveBalance(userId)
    );
  }

  /**
   * Cancel leave application
   */
  static async cancelLeave(leaveId: string): Promise<void> {
    return NetworkService.withInternetCheck(() =>
      apiClient.cancelLeave(leaveId)
    );
  }

  /**
   * Get pending leave approvals (for managers)
   */
  static async getPendingApprovals(): Promise<LeaveRecord[]> {
    return NetworkService.withInternetCheck(() =>
      apiClient.getPendingLeaveApprovals()
    );
  }

  /**
   * Approve or reject leave (for managers)
   */
  static async approveLeave(leaveId: string, approved: boolean, comments?: string): Promise<void> {
    return NetworkService.withInternetCheck(() =>
      apiClient.approveLeave(leaveId, approved, comments)
    );
  }

  /**
   * Calculate leave duration in days
   */
  static calculateLeaveDuration(startDate: string, endDate: string, halfDay?: boolean): number {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    
    if (halfDay) {
      return diffDays * 0.5;
    }
    
    return diffDays;
  }

  /**
   * Validate leave application
   */
  static validateLeaveApplication(leaveData: LeaveApplicationData): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    if (!leaveData.leaveType) {
      errors.push('Leave type is required');
    }
    
    if (!leaveData.startDate) {
      errors.push('Start date is required');
    }
    
    if (!leaveData.endDate) {
      errors.push('End date is required');
    }
    
    if (!leaveData.reason.trim()) {
      errors.push('Reason is required');
    }
    
    if (leaveData.startDate && leaveData.endDate) {
      const start = new Date(leaveData.startDate);
      const end = new Date(leaveData.endDate);
      
      if (start > end) {
        errors.push('Start date cannot be after end date');
      }
      
      if (start < new Date()) {
        errors.push('Start date cannot be in the past');
      }
    }
    
    if (leaveData.halfDay && !leaveData.halfDayType) {
      errors.push('Half day type is required for half day leave');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Get leave type display name
   */
  static getLeaveTypeDisplayName(leaveType: LeaveType): string {
    const displayNames: Record<LeaveType, string> = {
      'casual': 'Casual Leave',
      'sick': 'Sick Leave',
      'annual': 'Annual Leave',
      'maternity': 'Maternity Leave',
      'paternity': 'Paternity Leave',
      'bereavement': 'Bereavement Leave',
      'other': 'Other Leave',
    };
    
    return displayNames[leaveType] || leaveType;
  }

  /**
   * Get leave status display name
   */
  static getLeaveStatusDisplayName(status: string): string {
    const statusNames: Record<string, string> = {
      'pending': 'Pending',
      'approved': 'Approved',
      'rejected': 'Rejected',
      'cancelled': 'Cancelled',
    };
    
    return statusNames[status] || status;
  }
} 