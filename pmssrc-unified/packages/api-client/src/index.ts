import {
  LoginRequest,
  AuthResponse,
  User,
  AttendanceCreateRequest,
  AttendanceRecord,
  LeaveRequest,
  LeaveRecord,
  ReimbursementRequest,
  ReimbursementRecord,
  Organisation,
  TaxCalculationRequest,
  TaxCalculationResponse,
  ApiResponse,
  PaginatedResponse,
  LocationData
} from '@pmssrc/shared-types';

export class PMSApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL?: string) {
    this.baseURL = baseURL || this.getDefaultBaseURL();
  }

  private getDefaultBaseURL(): string {
    // Default to development server
    if (typeof window !== 'undefined') {
      // Web environment
      return process.env.REACT_APP_API_URL || 'http://localhost:8000';
    } else {
      // React Native environment
      return (global as any).__DEV__ 
        ? 'http://10.0.2.2:8000'  // Android emulator
        : 'https://your-production-api.com';
    }
  }

  // Authentication methods
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.post<AuthResponse>('/auth/login', credentials);
    this.token = response.access_token;
    return response;
  }

  async logout(): Promise<void> {
    await this.post('/auth/logout', {});
    this.token = null;
  }

  async validateToken(token: string): Promise<AuthResponse> {
    return this.post<AuthResponse>('/auth/validate', { token });
  }

  // Attendance methods
  async checkIn(attendanceData: AttendanceCreateRequest): Promise<AttendanceRecord> {
    return this.post<AttendanceRecord>('/attendance/check-in', attendanceData);
  }

  async checkOut(attendanceData: AttendanceCreateRequest): Promise<AttendanceRecord> {
    return this.post<AttendanceRecord>('/attendance/check-out', attendanceData);
  }

  async getAttendanceHistory(userId: string, startDate?: string, endDate?: string): Promise<AttendanceRecord[]> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    return this.get<AttendanceRecord[]>(`/attendance/history/${userId}?${params.toString()}`);
  }

  async getAttendanceAnalytics(userId: string, period: string): Promise<any> {
    return this.get<any>(`/attendance/analytics/${userId}?period=${period}`);
  }

  // Leave methods
  async applyLeave(leaveRequest: LeaveRequest): Promise<LeaveRecord> {
    return this.post<LeaveRecord>('/leaves/apply', leaveRequest);
  }

  async getLeaves(userId: string): Promise<LeaveRecord[]> {
    return this.get<LeaveRecord[]>(`/leaves/user/${userId}`);
  }

  async approveLeave(leaveId: string, approvedBy: string): Promise<LeaveRecord> {
    return this.put<LeaveRecord>(`/leaves/${leaveId}/approve`, { approvedBy });
  }

  async rejectLeave(leaveId: string, rejectedBy: string, reason: string): Promise<LeaveRecord> {
    return this.put<LeaveRecord>(`/leaves/${leaveId}/reject`, { rejectedBy, reason });
  }

  // Reimbursement methods
  async createReimbursementRequest(request: ReimbursementRequest): Promise<ReimbursementRecord> {
    return this.post<ReimbursementRecord>('/reimbursements/create', request);
  }

  async getReimbursements(userId: string): Promise<ReimbursementRecord[]> {
    return this.get<ReimbursementRecord[]>(`/reimbursements/user/${userId}`);
  }

  async approveReimbursement(reimbursementId: string, approvedBy: string): Promise<ReimbursementRecord> {
    return this.put<ReimbursementRecord>(`/reimbursements/${reimbursementId}/approve`, { approvedBy });
  }

  async rejectReimbursement(reimbursementId: string, rejectedBy: string, reason: string): Promise<ReimbursementRecord> {
    return this.put<ReimbursementRecord>(`/reimbursements/${reimbursementId}/reject`, { rejectedBy, reason });
  }

  // User methods
  async getUsers(organisationId?: string): Promise<User[]> {
    const params = organisationId ? `?organisation_id=${organisationId}` : '';
    return this.get<User[]>(`/users${params}`);
  }

  async getUserById(userId: string): Promise<User> {
    return this.get<User>(`/users/${userId}`);
  }

  async createUser(userData: Partial<User>): Promise<User> {
    return this.post<User>('/users/create', userData);
  }

  async updateUser(userId: string, userData: Partial<User>): Promise<User> {
    return this.put<User>(`/users/${userId}`, userData);
  }

  async deleteUser(userId: string): Promise<void> {
    return this.delete(`/users/${userId}`);
  }

  // Organisation methods
  async getOrganisations(): Promise<Organisation[]> {
    return this.get<Organisation[]>('/organisations');
  }

  async getOrganisationById(organisationId: string): Promise<Organisation> {
    return this.get<Organisation>(`/organisations/${organisationId}`);
  }

  async createOrganisation(organisationData: Partial<Organisation>): Promise<Organisation> {
    return this.post<Organisation>('/organisations/create', organisationData);
  }

  async updateOrganisation(organisationId: string, organisationData: Partial<Organisation>): Promise<Organisation> {
    return this.put<Organisation>(`/organisations/${organisationId}`, organisationData);
  }

  async deleteOrganisation(organisationId: string): Promise<void> {
    return this.delete(`/organisations/${organisationId}`);
  }

  // Taxation methods
  async calculateTax(taxRequest: TaxCalculationRequest): Promise<TaxCalculationResponse> {
    return this.post<TaxCalculationResponse>('/taxation/calculate', taxRequest);
  }

  async getTaxHistory(userId: string, financialYear?: string): Promise<TaxCalculationResponse[]> {
    const params = financialYear ? `?financial_year=${financialYear}` : '';
    return this.get<TaxCalculationResponse[]>(`/taxation/history/${userId}${params}`);
  }

  // Reporting methods
  async getDashboardAnalytics(userId: string): Promise<any> {
    return this.get<any>(`/reporting/dashboard/${userId}`);
  }

  async getAttendanceReport(organisationId: string, startDate: string, endDate: string): Promise<any> {
    const params = new URLSearchParams({
      organisation_id: organisationId,
      start_date: startDate,
      end_date: endDate
    });
    return this.get<any>(`/reporting/attendance?${params.toString()}`);
  }

  // Company Leave methods
  async getCompanyLeaves(organisationId: string): Promise<any[]> {
    return this.get<any[]>(`/company-leaves/${organisationId}`);
  }

  async createCompanyLeave(leaveData: any): Promise<any> {
    return this.post<any>('/company-leaves/create', leaveData);
  }

  async updateCompanyLeave(leaveId: string, leaveData: any): Promise<any> {
    return this.put<any>(`/company-leaves/${leaveId}`, leaveData);
  }

  async deleteCompanyLeave(leaveId: string): Promise<void> {
    return this.delete(`/company-leaves/${leaveId}`);
  }

  // Public Holiday methods
  async getPublicHolidays(year?: string): Promise<any[]> {
    const params = year ? `?year=${year}` : '';
    return this.get<any[]>(`/public-holidays${params}`);
  }

  async createPublicHoliday(holidayData: any): Promise<any> {
    return this.post<any>('/public-holidays/create', holidayData);
  }

  async updatePublicHoliday(holidayId: string, holidayData: any): Promise<any> {
    return this.put<any>(`/public-holidays/${holidayId}`, holidayData);
  }

  async deletePublicHoliday(holidayId: string): Promise<void> {
    return this.delete(`/public-holidays/${holidayId}`);
  }

  // Project Attributes methods
  async getProjectAttributes(organisationId: string): Promise<any[]> {
    return this.get<any[]>(`/project-attributes/${organisationId}`);
  }

  async createProjectAttribute(attributeData: any): Promise<any> {
    return this.post<any>('/project-attributes/create', attributeData);
  }

  async updateProjectAttribute(attributeId: string, attributeData: any): Promise<any> {
    return this.put<any>(`/project-attributes/${attributeId}`, attributeData);
  }

  async deleteProjectAttribute(attributeId: string): Promise<void> {
    return this.delete(`/project-attributes/${attributeId}`);
  }

  // LWP (Leave Without Pay) methods
  async getLWPRecords(userId: string): Promise<any[]> {
    return this.get<any[]>(`/lwp/user/${userId}`);
  }

  async createLWPRecord(lwpData: any): Promise<any> {
    return this.post<any>('/lwp/create', lwpData);
  }

  async updateLWPRecord(lwpId: string, lwpData: any): Promise<any> {
    return this.put<any>(`/lwp/${lwpId}`, lwpData);
  }

  async deleteLWPRecord(lwpId: string): Promise<void> {
    return this.delete(`/lwp/${lwpId}`);
  }

  // Export methods
  async exportAttendanceReport(organisationId: string, startDate: string, endDate: string, format: 'pdf' | 'excel'): Promise<Blob> {
    const params = new URLSearchParams({
      organisation_id: organisationId,
      start_date: startDate,
      end_date: endDate,
      format
    });
    return this.getBlob(`/export/attendance?${params.toString()}`);
  }

  async exportLeaveReport(organisationId: string, startDate: string, endDate: string, format: 'pdf' | 'excel'): Promise<Blob> {
    const params = new URLSearchParams({
      organisation_id: organisationId,
      start_date: startDate,
      end_date: endDate,
      format
    });
    return this.getBlob(`/export/leaves?${params.toString()}`);
  }

  // Utility methods
  setToken(token: string): void {
    this.token = token;
  }

  getToken(): string | null {
    return this.token;
  }

  // HTTP methods
  private async get<T>(endpoint: string): Promise<T> {
    const response = await this.request<T>(endpoint, {
      method: 'GET',
    });
    return response;
  }

  private async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response;
  }

  private async put<T>(endpoint: string, data: any): Promise<T> {
    const response = await this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return response;
  }

  private async delete(endpoint: string): Promise<void> {
    await this.request(endpoint, {
      method: 'DELETE',
    });
  }

  private async getBlob(endpoint: string): Promise<Blob> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.blob();
  }

  private async request<T>(endpoint: string, options: RequestInit): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...this.getHeaders(),
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {};
    
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    return headers;
  }
}

// Export a default instance
export const apiClient = new PMSApiClient(); 