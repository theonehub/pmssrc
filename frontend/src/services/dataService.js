import apiClient from '../utils/apiClient';

// Front-end service layer matching back-end FastAPI v2 routes
const dataService = {
  // User Management (Updated to v2 endpoints)
  async getUsers(skip = 0, limit = 10) {
    const response = await apiClient.get('/api/v2/users', { params: { skip, limit } });
    return response.data; // { total, users: [...] }
  },

  async getUserStats() {
    const response = await apiClient.get('/api/v2/users/stats');
    return response.data;
  },

  async getMyDirects() {
    const response = await apiClient.get('/api/v2/users/my/directs');
    return response.data;
  },

  async getManagerDirects(managerId) {
    const response = await apiClient.get('/api/v2/users/manager/directs', {
      params: { manager_id: managerId },
    });
    return response.data;
  },

  async getCurrentUser() {
    const response = await apiClient.get('/api/v2/users/me');
    return response.data;
  },

  async createUser(formData) {
    const response = await apiClient.post('/api/v2/users/create', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async importUsers(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/api/v2/users/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
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
