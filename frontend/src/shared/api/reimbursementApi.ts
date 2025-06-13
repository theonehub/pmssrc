import { BaseAPI } from './baseApi';

export interface ReimbursementRequest {
  request_id?: string;
  employee_id?: string;
  reimbursement_type_id: string;
  amount: number;
  description?: string;
  status?: 'draft' | 'submitted' | 'approved' | 'rejected';
  created_at?: string;
  updated_at?: string;
  receipt_file_name?: string;
  category_name?: string;
}

export interface ReimbursementType {
  type_id: string;
  category_name: string;
  description?: string;
  max_amount?: number;
  is_receipt_required: boolean;
  is_approval_required: boolean;
  is_active: boolean;
}

export interface ReimbursementResponse {
  success: boolean;
  data?: any;
  message?: string;
}

export class ReimbursementAPI {
  private baseApi: BaseAPI;

  constructor() {
    this.baseApi = BaseAPI.getInstance();
  }

  // Get my reimbursement requests
  async getMyRequests(): Promise<ReimbursementRequest[]> {
    const response = await this.baseApi.get('/api/v2/reimbursements/requests/my');
    return response.data || [];
  }

  // Get reimbursement types
  async getReimbursementTypes(): Promise<ReimbursementType[]> {
    const response = await this.baseApi.get('/api/v2/reimbursements/types');
    return response.data || [];
  }

  // Create reimbursement request
  async createRequest(data: Omit<ReimbursementRequest, 'request_id' | 'created_at' | 'updated_at'>): Promise<ReimbursementResponse> {
    const response = await this.baseApi.post('/api/v2/reimbursements/requests', data);
    return response;
  }

  // Create reimbursement request with file
  async createRequestWithFile(
    data: Omit<ReimbursementRequest, 'request_id' | 'created_at' | 'updated_at'>, 
    file: File
  ): Promise<ReimbursementResponse> {
    const formData = new FormData();
    
    // Append all data fields
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        formData.append(key, value.toString());
      }
    });
    
    // Append file
    formData.append('file', file);
    
    const response = await this.baseApi.post('/api/v2/reimbursements/requests/with-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response;
  }

  // Update reimbursement request
  async updateRequest(requestId: string, data: Partial<ReimbursementRequest>): Promise<ReimbursementResponse> {
    const response = await this.baseApi.put(`/api/v2/reimbursements/requests/${requestId}`, data);
    return response;
  }

  // Delete reimbursement request
  async deleteRequest(requestId: string): Promise<ReimbursementResponse> {
    const response = await this.baseApi.delete(`/api/v2/reimbursements/requests/${requestId}`);
    return response;
  }

  // Get specific request
  async getRequest(requestId: string): Promise<ReimbursementRequest> {
    const response = await this.baseApi.get(`/api/v2/reimbursements/requests/${requestId}`);
    return response.data;
  }

  // Download receipt
  downloadReceipt(requestId: string): void {
    // Open receipt in new tab/window
    const receiptUrl = `${this.baseApi.getBaseURL()}/api/v2/reimbursements/requests/${requestId}/receipt`;
    window.open(receiptUrl, '_blank');
  }

  // Get analytics/summary
  async getAnalytics(): Promise<any> {
    const response = await this.baseApi.get('/api/v2/reimbursements/analytics/summary');
    return response.data;
  }
}

// Export singleton instance
export const reimbursementApi = new ReimbursementAPI(); 