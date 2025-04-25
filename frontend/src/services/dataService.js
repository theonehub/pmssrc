import apiClient from '../utils/apiClient';

const dataService = {
  // Employee Management
  async getEmployees() {
    try {
      const response = await apiClient.get('/employees');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async getEmployeeById(id) {
    try {
      const response = await apiClient.get(`/employees/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async createEmployee(employeeData) {
    try {
      const response = await apiClient.post('/employees', employeeData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async updateEmployee(id, employeeData) {
    try {
      const response = await apiClient.put(`/employees/${id}`, employeeData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async deleteEmployee(id) {
    try {
      const response = await apiClient.delete(`/employees/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Payroll Management
  async getPayrolls() {
    try {
      const response = await apiClient.get('/payrolls');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async getPayrollById(id) {
    try {
      const response = await apiClient.get(`/payrolls/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async createPayroll(payrollData) {
    try {
      const response = await apiClient.post('/payrolls', payrollData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async updatePayroll(id, payrollData) {
    try {
      const response = await apiClient.put(`/payrolls/${id}`, payrollData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async deletePayroll(id) {
    try {
      const response = await apiClient.delete(`/payrolls/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Salary Management
  async getSalaries() {
    try {
      const response = await apiClient.get('/salaries');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async getSalaryById(id) {
    try {
      const response = await apiClient.get(`/salaries/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async createSalary(salaryData) {
    try {
      const response = await apiClient.post('/salaries', salaryData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async updateSalary(id, salaryData) {
    try {
      const response = await apiClient.put(`/salaries/${id}`, salaryData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async deleteSalary(id) {
    try {
      const response = await apiClient.delete(`/salaries/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Attendance Management
  async getAttendances() {
    try {
      const response = await apiClient.get('/attendances');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async getAttendanceById(id) {
    try {
      const response = await apiClient.get(`/attendances/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async createAttendance(attendanceData) {
    try {
      const response = await apiClient.post('/attendances', attendanceData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async updateAttendance(id, attendanceData) {
    try {
      const response = await apiClient.put(`/attendances/${id}`, attendanceData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async deleteAttendance(id) {
    try {
      const response = await apiClient.delete(`/attendances/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default dataService; 