import { apiClient } from '@pmssrc/api-client';
import { ReimbursementRequest, ReimbursementRecord, ReimbursementType } from '@pmssrc/shared-types';
import { NetworkService } from '../../../shared/utils/NetworkService';

export interface ReimbursementApplicationData {
  reimbursementType: ReimbursementType;
  amount: number;
  description: string;
  date: string;
  receipt?: string; // Base64 encoded receipt image
  category?: string;
  projectId?: string;
}

export interface ReimbursementStats {
  totalSubmitted: number;
  totalApproved: number;
  totalRejected: number;
  totalPending: number;
  totalAmount: number;
}

export class ReimbursementService {
  /**
   * Submit reimbursement request
   */
  static async submitReimbursement(userId: string, data: ReimbursementApplicationData): Promise<ReimbursementRecord> {
    return NetworkService.withInternetCheck(() =>
      apiClient.submitReimbursement({
        userId,
        reimbursementType: data.reimbursementType,
        amount: data.amount,
        description: data.description,
        date: data.date,
        receipt: data.receipt,
        category: data.category,
        projectId: data.projectId,
      })
    );
  }

  /**
   * Get user's reimbursement history
   */
  static async getReimbursementHistory(userId: string, startDate?: string, endDate?: string): Promise<ReimbursementRecord[]> {
    return NetworkService.withInternetCheck(() =>
      apiClient.getReimbursementHistory(userId, startDate, endDate)
    );
  }

  /**
   * Get reimbursement statistics
   */
  static async getReimbursementStats(userId: string): Promise<ReimbursementStats> {
    return NetworkService.withInternetCheck(() =>
      apiClient.getReimbursementStats(userId)
    );
  }

  /**
   * Cancel reimbursement request
   */
  static async cancelReimbursement(reimbursementId: string): Promise<void> {
    return NetworkService.withInternetCheck(() =>
      apiClient.cancelReimbursement(reimbursementId)
    );
  }

  /**
   * Get pending reimbursement approvals (for managers)
   */
  static async getPendingApprovals(): Promise<ReimbursementRecord[]> {
    return NetworkService.withInternetCheck(() =>
      apiClient.getPendingReimbursementApprovals()
    );
  }

  /**
   * Approve or reject reimbursement (for managers)
   */
  static async approveReimbursement(reimbursementId: string, approved: boolean, comments?: string): Promise<void> {
    return NetworkService.withInternetCheck(() =>
      apiClient.approveReimbursement(reimbursementId, approved, comments)
    );
  }

  /**
   * Get reimbursement types
   */
  static getReimbursementTypes(): { value: ReimbursementType; label: string }[] {
    return [
      { value: 'travel', label: 'Travel Expenses' },
      { value: 'meals', label: 'Meals & Food' },
      { value: 'office_supplies', label: 'Office Supplies' },
      { value: 'training', label: 'Training & Education' },
      { value: 'equipment', label: 'Equipment & Tools' },
      { value: 'software', label: 'Software & Subscriptions' },
      { value: 'other', label: 'Other Expenses' },
    ];
  }

  /**
   * Get expense categories
   */
  static getExpenseCategories(): string[] {
    return [
      'Transportation',
      'Accommodation',
      'Food & Beverages',
      'Office Supplies',
      'Training',
      'Equipment',
      'Software',
      'Marketing',
      'Client Entertainment',
      'Other',
    ];
  }

  /**
   * Validate reimbursement application
   */
  static validateReimbursementApplication(data: ReimbursementApplicationData): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    if (!data.reimbursementType) {
      errors.push('Reimbursement type is required');
    }
    
    if (!data.amount || data.amount <= 0) {
      errors.push('Amount must be greater than 0');
    }
    
    if (!data.description.trim()) {
      errors.push('Description is required');
    }
    
    if (!data.date) {
      errors.push('Date is required');
    }
    
    if (data.date) {
      const expenseDate = new Date(data.date);
      const today = new Date();
      
      if (expenseDate > today) {
        errors.push('Expense date cannot be in the future');
      }
    }
    
    if (data.amount > 10000) {
      errors.push('Amount cannot exceed ₹10,000');
    }
    
    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Get reimbursement type display name
   */
  static getReimbursementTypeDisplayName(type: ReimbursementType): string {
    const displayNames: Record<ReimbursementType, string> = {
      'travel': 'Travel Expenses',
      'meals': 'Meals & Food',
      'office_supplies': 'Office Supplies',
      'training': 'Training & Education',
      'equipment': 'Equipment & Tools',
      'software': 'Software & Subscriptions',
      'other': 'Other Expenses',
    };
    
    return displayNames[type] || type;
  }

  /**
   * Get reimbursement status display name
   */
  static getReimbursementStatusDisplayName(status: string): string {
    const statusNames: Record<string, string> = {
      'pending': 'Pending',
      'approved': 'Approved',
      'rejected': 'Rejected',
      'cancelled': 'Cancelled',
    };
    
    return statusNames[status] || status;
  }

  /**
   * Format currency
   */
  static formatCurrency(amount: number): string {
    return `₹${amount.toLocaleString('en-IN')}`;
  }

  /**
   * Calculate total reimbursement amount
   */
  static calculateTotalAmount(reimbursements: ReimbursementRecord[]): number {
    return reimbursements.reduce((total, reimbursement) => {
      if (reimbursement.status === 'approved') {
        return total + reimbursement.amount;
      }
      return total;
    }, 0);
  }
} 