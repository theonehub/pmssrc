import apiClient from '../utils/apiClient';

// Helper functions for data mapping between frontend and backend v2 formats
const transformBackendToFrontend = (backendUser) => {
  if (!backendUser) {
    if (process.env.NODE_ENV === 'development') {
      console.warn('No backend user data provided');
    }
    return null;
  }
  // Support both UserResponseDTO (detailed) and UserSummaryDTO (list view)
  const isSummary = !backendUser.personal_details && !backendUser.documents && !backendUser.bank_details;
  const transformed = {
    employee_id: backendUser.employee_id || backendUser.emp_id || '',
    name: backendUser.name || '',
    email: backendUser.email || '',
    mobile: isSummary ? backendUser.mobile || '' : backendUser.personal_details?.mobile || backendUser.mobile || '',
    gender: isSummary ? backendUser.gender || '' : backendUser.personal_details?.gender || backendUser.gender || '',
    date_of_birth: isSummary ? backendUser.date_of_birth || '' : backendUser.personal_details?.date_of_birth || backendUser.date_of_birth || backendUser.dob || '',
    date_of_joining: backendUser.date_of_joining || backendUser.doj || '',
    role: backendUser.role || backendUser.permissions?.role || '',
    department: backendUser.department || '',
    designation: backendUser.designation || '',
    manager_id: backendUser.manager_id || '',
    address: backendUser.address || '',
    emergency_contact: backendUser.emergency_contact || '',
    blood_group: backendUser.blood_group || '',
    location: backendUser.location || '',
    pan_number: isSummary ? backendUser.pan_number || '' : backendUser.personal_details?.pan_number || backendUser.pan_number || '',
    aadhar_number: isSummary ? backendUser.aadhar_number || '' : backendUser.personal_details?.aadhar_number || backendUser.aadhar_number || '',
    uan_number: isSummary ? backendUser.uan_number || '' : backendUser.personal_details?.uan_number || backendUser.uan_number || '',
    esi_number: isSummary ? backendUser.esi_number || '' : backendUser.personal_details?.esi_number || backendUser.esi_number || '',
    created_at: backendUser.created_at || '',
    updated_at: backendUser.updated_at || '',
    is_active: backendUser.is_active !== undefined ? backendUser.is_active : true,
    status: backendUser.status || (backendUser.is_active ? 'active' : 'inactive'),
    profile_picture_url: backendUser.profile_picture_url || '',
    pan_document_path: backendUser.documents?.pan_document_path || backendUser.pan_document_path || '',
    aadhar_document_path: backendUser.documents?.aadhar_document_path || backendUser.aadhar_document_path || '',
    photo_path: backendUser.documents?.photo_path || backendUser.photo_path || '',
    // Bank Details
    bank_account_number: backendUser.bank_details?.account_number || backendUser.bank_account_number || '',
    bank_name: backendUser.bank_details?.bank_name || backendUser.bank_name || '',
    ifsc_code: backendUser.bank_details?.ifsc_code || backendUser.ifsc_code || '',
    account_holder_name: backendUser.bank_details?.account_holder_name || backendUser.account_holder_name || '',
    branch_name: backendUser.bank_details?.branch_name || backendUser.branch_name || '',
    account_type: backendUser.bank_details?.account_type || backendUser.account_type || ''
  };
  return transformed;
};

const transformFrontendToBackend = (frontendUser) => {
  return {
    employee_id: frontendUser.employee_id || frontendUser.emp_id,
    name: frontendUser.name,
    email: frontendUser.email,
    mobile: frontendUser.mobile,
    password: frontendUser.password,
    role: frontendUser.role,
    department: frontendUser.department,
    designation: frontendUser.designation,
    manager_id: frontendUser.manager_id,
    date_of_birth: frontendUser.date_of_birth || frontendUser.dob,
    date_of_joining: frontendUser.date_of_joining || frontendUser.doj,
    gender: frontendUser.gender,
    address: frontendUser.address,
    emergency_contact: frontendUser.emergency_contact,
    blood_group: frontendUser.blood_group,
    location: frontendUser.location,
    pan_number: frontendUser.pan_number,
    aadhar_number: frontendUser.aadhar_number,
    uan_number: frontendUser.uan_number,
    esi_number: frontendUser.esi_number,
    // Bank Details
    bank_account_number: frontendUser.bank_account_number,
    bank_name: frontendUser.bank_name,
    ifsc_code: frontendUser.ifsc_code,
    account_holder_name: frontendUser.account_holder_name,
    branch_name: frontendUser.branch_name,
    account_type: frontendUser.account_type,
  };
};

// Front-end service layer matching back-end FastAPI v2 routes
const dataService = {
  // User Management (Updated to v2 endpoints)
  async getUsers(skip = 0, limit = 10, include_inactive = false, include_deleted = false, organisation_id = null) {
    const response = await apiClient.get('/api/v2/users', { 
      params: { 
        skip, 
        limit, 
        include_inactive, 
        include_deleted,
        organisation_id 
      } 
    });
    
    // Map the response to frontend format
    const mappedUsers = response.data.users?.map(transformBackendToFrontend) || [];
    return {
      total: response.data.total,
      users: mappedUsers,
      skip: response.data.skip || skip,
      limit: response.data.limit || limit
    };
  },

  async getUserById(userId) {
    const response = await apiClient.get(`/api/v2/users/${userId}`);
    const mappedUser = transformBackendToFrontend(response.data);
    
    if (!mappedUser) {
      throw new Error('User data not found or invalid');
    }
    return mappedUser;
  },

  async getUserByEmail(email) {
    const response = await apiClient.get(`/api/v2/users/email/${email}`);
    const mappedUser = transformBackendToFrontend(response.data);
    if (!mappedUser) {
      throw new Error('User data not found or invalid');
    }
    return mappedUser;
  },

  async getUserStats() {
    const response = await apiClient.get('/api/v2/users/stats');
    return response.data;
  },

  async getMyDirects() {
    const response = await apiClient.get('/api/v2/users/my/directs');
    return response.data.map(transformBackendToFrontend);
  },

  async getManagerDirects(managerId) {
    const response = await apiClient.get('/api/v2/users/manager/directs', {
      params: { manager_id: managerId },
    });
    return response.data.map(transformBackendToFrontend);
  },

  async getCurrentUser() {
    const response = await apiClient.get('/api/v2/users/me');
    return transformBackendToFrontend(response.data);
  },

  async createUser(userData) {
    const backendData = transformFrontendToBackend(userData);
    const response = await apiClient.post('/api/v2/users/create', backendData);
    return transformBackendToFrontend(response.data);
  },

  async createUserWithFiles(userData, files = {}) {
    const formData = new FormData();
    formData.append('user_data', JSON.stringify(transformFrontendToBackend(userData)));
    
    if (files.pan_file) {
      formData.append('pan_file', files.pan_file);
    }
    if (files.aadhar_file) {
      formData.append('aadhar_file', files.aadhar_file);
    }
    if (files.photo) {
      formData.append('photo', files.photo);
    }

    const response = await apiClient.post('/api/v2/users/with-files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return transformBackendToFrontend(response.data);
  },

  async updateUser(userId, userData) {
    const backendData = transformFrontendToBackend(userData);
    const response = await apiClient.put(`/api/v2/users/${userId}`, backendData);
    return transformBackendToFrontend(response.data);
  },

  async updateUserLegacy(empId, userData) {
    const backendData = transformFrontendToBackend(userData);
    const response = await apiClient.put(`/api/v2/users/${empId}`, backendData);
    return transformBackendToFrontend(response.data);
  },

  async deleteUser(empId) {
    const response = await apiClient.delete(`/api/v2/users/${empId}`);
    return response.data;
  },

  async changeUserPassword(userId, passwordData) {
    const response = await apiClient.patch(`/api/v2/users/${userId}/password`, passwordData);
    return transformBackendToFrontend(response.data);
  },

  async changeUserRole(userId, roleData) {
    const response = await apiClient.patch(`/api/v2/users/${userId}/role`, roleData);
    return transformBackendToFrontend(response.data);
  },

  async updateUserStatus(userId, statusData) {
    const response = await apiClient.patch(`/api/v2/users/${userId}/status`, statusData);
    return transformBackendToFrontend(response.data);
  },

  async checkUserExists(email = null, mobile = null, pan_number = null, exclude_id = null) {
    const response = await apiClient.get('/api/v2/users/check/exists', {
      params: { email, mobile, pan_number, exclude_id }
    });
    return response.data;
  },

  async searchUsers(filters) {
    const response = await apiClient.post('/api/v2/users/search', filters);
    const mappedUsers = response.data.users?.map(transformBackendToFrontend) || [];
    return {
      ...response.data,
      users: mappedUsers
    };
  },

  async getUserStatistics() {
    const response = await apiClient.get('/api/v2/users/analytics/statistics');
    return response.data;
  },

  async importUsers(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/api/v2/users/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async downloadUserTemplate() {
    const response = await apiClient.get('/api/v2/users/template', {
      params: { format: 'csv' },
      responseType: 'blob'
    });
    return response.data;
  },

  async loginUser(credentials) {
    const response = await apiClient.post('/api/v2/users/auth/login', credentials);
    return response.data;
  },

  // Legacy compatibility methods
  async getAllUsersLegacy(hostname) {
    const response = await apiClient.get('/api/v2/users/legacy/all', {
      params: { hostname }
    });
    return response.data.map(transformBackendToFrontend);
  },

  async getUserByEmpIdLegacy(empId, hostname) {
    const response = await apiClient.get(`/api/v2/users/legacy/${empId}`, {
      params: { hostname }
    });
    const mappedUser = transformBackendToFrontend(response.data);
    if (!mappedUser) {
      throw new Error('User data not found or invalid');
    }
    return mappedUser;
  },

  // Attendance Management (Updated to v2 endpoints)
  async checkin() {
    const response = await apiClient.post('/api/v2/attendance/checkin');
    return response.data;
  },

  async checkout() {
    const response = await apiClient.post('/api/v2/attendance/checkout');
    return response.data;
  },

  async getEmployeeAttendanceByMonth(empId, month, year) {
    const response = await apiClient.get(
      `/api/v2/attendance/user/${empId}/${month}/${year}`
    );
    return response.data;
  },

  async getMyAttendanceByMonth(month, year) {
    const response = await apiClient.get(
      `/api/v2/attendance/my/month/${month}/${year}`
    );
    return response.data;
  },

  async getMyAttendanceByYear(year) {
    const response = await apiClient.get(`/api/v2/attendance/my/year/${year}`);
    return response.data;
  },

  async getTeamAttendanceByDate(date, month, year) {
    const response = await apiClient.get(
      `/api/v2/attendance/manager/date/${date}/${month}/${year}`
    );
    return response.data;
  },

  async getTeamAttendanceByMonth(month, year) {
    const response = await apiClient.get(
      `/api/v2/attendance/manager/month/${month}/${year}`
    );
    return response.data;
  },

  async getTeamAttendanceByYear(year) {
    const response = await apiClient.get(`/api/v2/attendance/manager/year/${year}`);
    return response.data;
  },

  async getAdminAttendanceByDate(date, month, year) {
    const response = await apiClient.get(
      `/api/v2/attendance/admin/date/${date}/${month}/${year}`
    );
    return response.data;
  },

  async getAdminAttendanceByMonth(month, year) {
    const response = await apiClient.get(
      `/api/v2/attendance/admin/month/${month}/${year}`
    );
    return response.data;
  },

  async getAdminAttendanceByYear(year) {
    const response = await apiClient.get(`/api/v2/attendance/admin/year/${year}`);
    return response.data;
  },

  async getAttendanceStatsToday() {
    const response = await apiClient.get('/api/v2/attendance/stats/today');
    return response.data;
  },

  // Taxation Management (Updated to v2 endpoints)
  async getAllTaxation() {
    const response = await apiClient.get('/api/v2/taxation/all-taxation');
    return response.data;
  },

  async getTaxationByEmpId(empId) {
    const response = await apiClient.get(`/api/v2/taxation/taxation/${empId}`);
    return response.data;
  },

  async getMyTaxation() {
    const response = await apiClient.get('/api/v2/taxation/my-taxation');
    return response.data;
  },

  async saveTaxationData(taxationData) {
    const response = await apiClient.post('/api/v2/taxation/save-taxation-data', taxationData);
    return response.data;
  },

  async computeVrsValue(empId, vrsData) {
    const response = await apiClient.post(`/api/v2/taxation/compute-vrs-value/${empId}`, vrsData);
    return response.data;
  },

  // Payout Management (Updated to v2 endpoints)
  async calculateMonthlyPayout(payoutData) {
    const response = await apiClient.post('/api/v2/payouts/calculate', payoutData);
    return response.data;
  },

  async createPayout(payoutData) {
    const response = await apiClient.post('/api/v2/payouts/create', payoutData);
    return response.data;
  },

  async getEmployeePayouts(employeeId) {
    const response = await apiClient.get(`/api/v2/payouts/employee/${employeeId}`);
    return response.data;
  },

  async getMyPayouts() {
    const response = await apiClient.get('/api/v2/payouts/my-payouts');
    return response.data;
  },

  async updatePayout(payoutId, payoutData) {
    const response = await apiClient.put(`/api/v2/payouts/${payoutId}`, payoutData);
    return response.data;
  },

  async bulkProcessPayouts(payoutIds) {
    const response = await apiClient.post('/api/v2/payouts/bulk-process', { payout_ids: payoutIds });
    return response.data;
  },
};

export default dataService;
