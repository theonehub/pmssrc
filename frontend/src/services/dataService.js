import apiClient from '../utils/apiClient';

// Front-end service layer matching back-end FastAPI routes
const dataService = {
  // User Management
  async getUsers(skip = 0, limit = 10) {
    const response = await apiClient.get('/users', { params: { skip, limit } });
    return response.data;  // { total, users: [...] }
  },

  async getUserStats() {
    const response = await apiClient.get('/users/stats');
    return response.data;
  },

  async getMyDirects() {
    const response = await apiClient.get('/users/my/directs');
    return response.data;
  },

  async getManagerDirects(managerId) {
    const response = await apiClient.get('/users/manager/directs', { params: { manager_id: managerId } });
    return response.data;
  },

  async getCurrentUser() {
    const response = await apiClient.get('/users/me');
    return response.data;
  },

  async createUser(formData) {
    const response = await apiClient.post(
      '/users/create',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  async importUsers(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post(
      '/users/import',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    return response.data;
  },

  // Salary Computation
  async getSalaryComputation() {
    const response = await apiClient.get('/salary-computation');
    return response.data;
  },

  // Salary Components
  async getSalaryComponents() {
    const response = await apiClient.get('/salary-components');
    return response.data;
  },

  async getSalaryComponentById(sc_id) {
    const response = await apiClient.get(`/salary-components/${sc_id}`);
    return response.data;
  },

  async createSalaryComponent(data) {
    const response = await apiClient.post('/salary-components', data);
    return response.data;
  },

  async updateSalaryComponent(sc_id, data) {
    const response = await apiClient.put(`/salary-components/${sc_id}`, data);
    return response.data;
  },

  async deleteSalaryComponent(sc_id) {
    const response = await apiClient.delete(`/salary-components/${sc_id}`);
    return response.data;
  },

  async getSalaryComponentAssignments(emp_id) {
    const response = await apiClient.get(`/salary-components/assignments/${emp_id}`);
    return response.data;
  },

  async createSalaryComponentAssignments(emp_id, components) {
    const response = await apiClient.post(
      `/salary-components/assignments/${emp_id}`,
      components
    );
    return response.data;
  },

  async getSalaryComponentDeclarations(emp_id) {
    const response = await apiClient.get(`/salary-components/declarations/${emp_id}`);
    return response.data;
  },

  async createSalaryComponentDeclarations(emp_id, components) {
    const response = await apiClient.post(
      `/salary-components/declarations/${emp_id}`,
      components
    );
    return response.data;
  },

  // Employee Salary
  async createEmployeeSalary(data) {
    const response = await apiClient.post('/employee-salary', data);
    return response.data;
  },

  async getEmployeeSalary(employeeId) {
    const response = await apiClient.get(`/employee-salary/${employeeId}`);
    return response.data;
  },

  async updateEmployeeSalary(salaryId, data) {
    const response = await apiClient.put(`/employee-salary/${salaryId}`, data);
    return response.data;
  },

  async deleteEmployeeSalary(salaryId) {
    const response = await apiClient.delete(`/employee-salary/${salaryId}`);
    return response.data;
  },

  async checkSalaryAssignmentStatus(employeeId) {
    const response = await apiClient.get(`/employee-salary/status/${employeeId}`);
    return response.data;
  },

  async assignSalaryStructure(employeeId, components) {
    const response = await apiClient.post(
      `/employee-salary/${employeeId}/salary-structure`,
      { components }
    );
    return response.data;
  },

  async getSalaryStructure(employeeId) {
    const response = await apiClient.get(
      `/employee-salary/${employeeId}/salary-structure`
    );
    return response.data;
  },

  async getSalaryStructureView(employeeId) {
    const response = await apiClient.get(
      `/employee-salary/${employeeId}/salary-structure/view`
    );
    return response.data;
  },

  // Attendance Management
  async checkin() {
    const response = await apiClient.post('/attendance/checkin');
    return response.data;
  },

  async checkout() {
    const response = await apiClient.post('/attendance/checkout');
    return response.data;
  },

  async getAllAttendance() {
    const response = await apiClient.post('/attendance/all');
    return response.data;
  },

  async getEmployeeAttendanceByMonth(empId, month, year) {
    const response = await apiClient.get(
      `/attendance/user/${empId}/${month}/${year}`
    );
    return response.data;
  },

  async getMyAttendanceByMonth(month, year) {
    const response = await apiClient.get(
      `/attendance/my/month/${month}/${year}`
    );
    return response.data;
  },

  async getMyAttendanceByYear(year) {
    const response = await apiClient.get(
      `/attendance/my/year/${year}`
    );
    return response.data;
  },

  async getTeamAttendanceByDate(date, month, year) {
    const response = await apiClient.get(
      `/attendance/manager/date/${date}/${month}/${year}`
    );
    return response.data;
  },

  async getTeamAttendanceByMonth(month, year) {
    const response = await apiClient.get(
      `/attendance/manager/month/${month}/${year}`
    );
    return response.data;
  },

  async getTeamAttendanceByYear(year) {
    const response = await apiClient.get(
      `/attendance/manager/year/${year}`
    );
    return response.data;
  },

  async getAdminAttendanceByDate(date, month, year) {
    const response = await apiClient.get(
      `/attendance/admin/date/${date}/${month}/${year}`
    );
    return response.data;
  },

  async getAdminAttendanceByMonth(month, year) {
    const response = await apiClient.get(
      `/attendance/admin/month/${month}/${year}`
    );
    return response.data;
  },

  async getAdminAttendanceByYear(year) {
    const response = await apiClient.get(
      `/attendance/admin/year/${year}`
    );
    return response.data;
  },

  async getAttendanceStatsToday() {
    const response = await apiClient.get('/attendance/stats/today');
    return response.data;
  }
};

export default dataService; 