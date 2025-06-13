import { get, post, put, del } from './baseApi';

// Type definitions based on backend DTOs and component usage
export interface ReimbursementType {
  type_id: string;
  category_name: string;
  description?: string;
  max_limit?: number;
  is_approval_required: boolean;
  is_receipt_required: boolean;
  is_active: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ReimbursementSummary {
  request_id: string;
  employee_id: string;
  category_name: string;
  amount: number;
  status: string;
  submitted_at?: string;
  final_amount?: number;
  receipt_file_name?: string;
  receipt_uploaded_at?: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface CreateReimbursementRequest {
  employee_id: string;
  reimbursement_type_id: string;
  amount: number;
  description?: string;
  currency?: string;
}

export interface UpdateReimbursementRequest {
  amount?: number;
  description?: string;
}

export interface CreateReimbursementType {
  category_name: string;
  description?: string;
  max_limit?: number;
  is_approval_required: boolean;
  is_receipt_required: boolean;
}

export interface UpdateReimbursementType {
  category_name?: string;
  description?: string;
  max_limit?: number;
}

export interface ReimbursementResponse {
  request_id: string;
  employee_id: string;
  reimbursement_type: ReimbursementType;
  amount: number;
  description?: string;
  status: string;
  created_at: string;
  updated_at: string;
  submitted_at?: string;
  receipt_file_name?: string;
  receipt_uploaded_at?: string;
  approved_by?: string;
  approved_at?: string;
  approved_amount?: number;
  approval_comments?: string;
  rejection_comments?: string;
  rejected_by?: string;
  rejected_at?: string;
  paid_by?: string;
  paid_at?: string;
  payment_method?: string;
  payment_reference?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success?: boolean;
}

/**
 * Reimbursement service for handling reimbursement-related API calls
 * Uses v2 API endpoints for consistency with backend
 */
class ReimbursementService {
  private readonly baseUrl = '/api/v2/reimbursements';

  // ==================== REIMBURSEMENT REQUEST OPERATIONS ====================

  /**
   * Create a new reimbursement request
   * @param request - Reimbursement request data
   * @returns Promise with reimbursement response
   */
  async createReimbursementRequest(request: CreateReimbursementRequest): Promise<ApiResponse<ReimbursementResponse>> {
    try {
      const response = await post<ReimbursementResponse>(`${this.baseUrl}/requests`, request);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error creating reimbursement request:', error);
      }
      throw error;
    }
  }

  /**
   * Create a new reimbursement request with file upload
   * @param request - Reimbursement request data
   * @param file - Receipt file
   * @returns Promise with reimbursement response
   */
  async createReimbursementRequestWithFile(
    request: CreateReimbursementRequest,
    file: File
  ): Promise<ApiResponse<ReimbursementResponse>> {
    try {
      const formData = new FormData();
      formData.append('reimbursement_type_id', request.reimbursement_type_id);
      formData.append('amount', request.amount.toString());
      formData.append('description', request.description || '');
      formData.append('file', file);

      const response = await post<ReimbursementResponse>(
        `${this.baseUrl}/requests/with-file`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error creating reimbursement request with file:', error);
      }
      throw error;
    }
  }

  /**
   * Get current user's reimbursement requests
   * @param status - Optional status filter
   * @param limit - Number of requests to return
   * @param offset - Number of requests to skip
   * @returns Promise with list of reimbursement summaries
   */
  async getMyReimbursements(
    status?: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<ApiResponse<ReimbursementSummary[]>> {
    try {
      const params = new URLSearchParams();
      if (status) params.append('status', status);
      params.append('limit', limit.toString());
      params.append('offset', offset.toString());

      const response = await get<ReimbursementSummary[]>(
        `${this.baseUrl}/requests/my?${params.toString()}`
      );
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error getting my reimbursements:', error);
      }
      throw error;
    }
  }

  /**
   * Get a specific reimbursement request by ID
   * @param requestId - Reimbursement request ID
   * @returns Promise with reimbursement response
   */
  async getReimbursementRequest(requestId: string): Promise<ApiResponse<ReimbursementResponse>> {
    try {
      const response = await get<ReimbursementResponse>(`${this.baseUrl}/requests/${requestId}`);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error getting reimbursement request:', error);
      }
      throw error;
    }
  }

  /**
   * Update a reimbursement request
   * @param requestId - Reimbursement request ID
   * @param request - Updated request data
   * @returns Promise with reimbursement response
   */
  async updateReimbursementRequest(
    requestId: string,
    request: UpdateReimbursementRequest
  ): Promise<ApiResponse<ReimbursementResponse>> {
    try {
      const response = await put<ReimbursementResponse>(`${this.baseUrl}/requests/${requestId}`, request);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error updating reimbursement request:', error);
      }
      throw error;
    }
  }

  /**
   * Delete a reimbursement request
   * @param requestId - Reimbursement request ID
   * @returns Promise with success message
   */
  async deleteReimbursementRequest(requestId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await del<{ message: string }>(`${this.baseUrl}/requests/${requestId}`);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error deleting reimbursement request:', error);
      }
      throw error;
    }
  }

  /**
   * Approve a reimbursement request
   * @param requestId - Reimbursement request ID
   * @param approvalData - Approval data
   * @returns Promise with reimbursement response
   */
  async approveReimbursementRequest(
    requestId: string,
    approvalData: { approved_amount?: number; comments?: string }
  ): Promise<ApiResponse<ReimbursementResponse>> {
    try {
      const response = await put<ReimbursementResponse>(
        `${this.baseUrl}/requests/${requestId}/approve`,
        approvalData
      );
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error approving reimbursement request:', error);
      }
      throw error;
    }
  }

  /**
   * Reject a reimbursement request
   * @param requestId - Reimbursement request ID
   * @param rejectionData - Rejection data
   * @returns Promise with reimbursement response
   */
  async rejectReimbursementRequest(
    requestId: string,
    rejectionData: { comments: string }
  ): Promise<ApiResponse<ReimbursementResponse>> {
    try {
      const response = await put<ReimbursementResponse>(
        `${this.baseUrl}/requests/${requestId}/reject`,
        rejectionData
      );
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error rejecting reimbursement request:', error);
      }
      throw error;
    }
  }

  // ==================== REIMBURSEMENT TYPE OPERATIONS ====================

  /**
   * Get all reimbursement types
   * @param activeOnly - Whether to return only active types
   * @returns Promise with list of reimbursement types
   */
  async getReimbursementTypes(activeOnly: boolean = true): Promise<ApiResponse<ReimbursementType[]>> {
    try {
      const params = new URLSearchParams();
      params.append('active_only', activeOnly.toString());

      const response = await get<ReimbursementType[]>(`${this.baseUrl}/types?${params.toString()}`);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error getting reimbursement types:', error);
      }
      throw error;
    }
  }

  /**
   * Get a specific reimbursement type by ID
   * @param typeId - Reimbursement type ID
   * @returns Promise with reimbursement type
   */
  async getReimbursementType(typeId: string): Promise<ApiResponse<ReimbursementType>> {
    try {
      const response = await get<ReimbursementType>(`${this.baseUrl}/types/${typeId}`);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error getting reimbursement type:', error);
      }
      throw error;
    }
  }

  /**
   * Create a new reimbursement type
   * @param typeData - Reimbursement type data
   * @returns Promise with reimbursement type response
   */
  async createReimbursementType(typeData: CreateReimbursementType): Promise<ApiResponse<ReimbursementType>> {
    try {
      const response = await post<ReimbursementType>(`${this.baseUrl}/types`, typeData);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error creating reimbursement type:', error);
      }
      throw error;
    }
  }

  /**
   * Update a reimbursement type
   * @param typeId - Reimbursement type ID
   * @param typeData - Updated type data
   * @returns Promise with reimbursement type response
   */
  async updateReimbursementType(
    typeId: string,
    typeData: UpdateReimbursementType
  ): Promise<ApiResponse<ReimbursementType>> {
    try {
      const response = await put<ReimbursementType>(`${this.baseUrl}/types/${typeId}`, typeData);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error updating reimbursement type:', error);
      }
      throw error;
    }
  }

  /**
   * Delete (deactivate) a reimbursement type
   * @param typeId - Reimbursement type ID
   * @returns Promise with success message
   */
  async deleteReimbursementType(typeId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await del<{ message: string }>(`${this.baseUrl}/types/${typeId}`);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error deleting reimbursement type:', error);
      }
      throw error;
    }
  }

  // ==================== MANAGEMENT OPERATIONS ====================

  /**
   * Get pending reimbursement requests (for managers/admins)
   * @param limit - Number of requests to return
   * @param offset - Number of requests to skip
   * @returns Promise with list of pending reimbursement summaries
   */
  async getPendingReimbursements(
    limit: number = 50,
    offset: number = 0
  ): Promise<ApiResponse<ReimbursementSummary[]>> {
    try {
      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      params.append('offset', offset.toString());

      const response = await get<ReimbursementSummary[]>(
        `${this.baseUrl}/requests/pending?${params.toString()}`
      );
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error getting pending reimbursements:', error);
      }
      throw error;
    }
  }

  /**
   * Get approved reimbursement requests (for managers/admins)
   * @param limit - Number of requests to return
   * @param offset - Number of requests to skip
   * @returns Promise with list of approved reimbursement summaries
   */
  async getApprovedReimbursements(
    limit: number = 50,
    offset: number = 0
  ): Promise<ApiResponse<ReimbursementSummary[]>> {
    try {
      const params = new URLSearchParams();
      params.append('limit', limit.toString());
      params.append('offset', offset.toString());

      const response = await get<ReimbursementSummary[]>(
        `${this.baseUrl}/requests/approved?${params.toString()}`
      );
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error getting approved reimbursements:', error);
      }
      throw error;
    }
  }

  // ==================== ANALYTICS OPERATIONS ====================

  /**
   * Get reimbursement analytics
   * @param startDate - Start date for filtering (YYYY-MM-DD)
   * @param endDate - End date for filtering (YYYY-MM-DD)
   * @returns Promise with analytics data
   */
  async getReimbursementAnalytics(
    startDate?: string,
    endDate?: string
  ): Promise<ApiResponse<any>> {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await get<any>(`${this.baseUrl}/analytics/summary?${params.toString()}`);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error getting reimbursement analytics:', error);
      }
      throw error;
    }
  }

  // ==================== FILE OPERATIONS ====================

  /**
   * Download receipt for a reimbursement request
   * @param requestId - Reimbursement request ID
   * @returns Promise with file download
   */
  async downloadReceipt(requestId: string): Promise<void> {
    try {
      // This would typically trigger a file download
      const url = `${this.baseUrl}/requests/${requestId}/receipt`;
      window.open(url, '_blank');
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error downloading receipt:', error);
      }
      throw error;
    }
  }

  // ==================== HEALTH CHECK ====================

  /**
   * Health check for reimbursement service
   * @returns Promise with health status
   */
  async healthCheck(): Promise<ApiResponse<any>> {
    try {
      const response = await get<any>(`${this.baseUrl}/health`);
      return { data: response, success: true };
    } catch (error: any) {
      if (process.env.NODE_ENV === 'development') {
        console.error('Error in reimbursement service health check:', error);
      }
      throw error;
    }
  }
}

// Create and export service instance
const reimbursementService = new ReimbursementService();

export default reimbursementService;

// Types are already exported above with the interface declarations 