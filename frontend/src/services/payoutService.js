import apiClient from '../utils/apiClient';

export const payoutService = {
  // Employee payout services (Updated to v2 endpoints)
  getEmployeePayouts: async (employeeId, year = null, month = null) => {
    try {
      let url = `/api/v2/payouts/employee/${employeeId}`;
      const params = new URLSearchParams();

      if (year) params.append('year', year);
      if (month) params.append('month', month);

      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await apiClient.get(url);
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching employee payouts:', error);
      }
      throw error;
    }
  },

  // Get current user's payouts (using v2 endpoint)
  getMyPayouts: async (year = null, month = null) => {
    try {
      let url = `/api/v2/payouts/my-payouts`;
      const params = new URLSearchParams();

      if (year) params.append('year', year);
      if (month) params.append('month', month);

      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await apiClient.get(url);
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching my payouts:', error);
      }
      throw error;
    }
  },

  // Get payout by ID
  getPayoutById: async payoutId => {
    try {
      const response = await apiClient.get(`/api/v2/payouts/${payoutId}`);
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching payout by ID:', error);
      }
      throw error;
    }
  },

  // Calculate monthly payout
  calculateMonthlyPayout: async (
    employeeId,
    month,
    year,
    overrideSalary = null
  ) => {
    try {
      const params = new URLSearchParams({
        employee_id: employeeId,
        month,
        year,
      });

      let requestBody = null;
      if (overrideSalary) {
        requestBody = overrideSalary;
      }

      const response = await apiClient.post(
        `/api/v2/payouts/calculate?${params.toString()}`,
        requestBody
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error calculating monthly payout:', error);
      }
      throw error;
    }
  },

  // Create payout
  createPayout: async payoutData => {
    try {
      const response = await apiClient.post('/api/v2/payouts/create', payoutData);
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error creating payout:', error);
      }
      throw error;
    }
  },

  // Update payout
  updatePayout: async (payoutId, updateData) => {
    try {
      const response = await apiClient.put(
        `/api/v2/payouts/${payoutId}`,
        updateData
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error updating payout:', error);
      }
      throw error;
    }
  },

  // Update payout status
  updatePayoutStatus: async (payoutId, status) => {
    try {
      const response = await apiClient.put(
        `/api/v2/payouts/${payoutId}/status`,
        status
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error updating payout status:', error);
      }
      throw error;
    }
  },

  // Auto-generate current month payout
  autoGenerateCurrentMonthPayout: async employeeId => {
    try {
      const response = await apiClient.post(
        `/api/v2/payouts/auto-generate/${employeeId}`
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error auto-generating payout:', error);
      }
      throw error;
    }
  },

  // Bulk process payouts
  bulkProcessPayouts: async request => {
    try {
      const response = await apiClient.post(
        '/api/v2/payouts/bulk-process',
        request
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error in bulk payout processing:', error);
      }
      throw error;
    }
  },

  // Get monthly payouts (admin)
  getMonthlyPayouts: async (year, month, status = null) => {
    try {
      let url = `/api/v2/payouts/monthly/${year}/${month}`;
      if (status) {
        url += `?status=${status}`;
      }

      const response = await apiClient.get(url);
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching monthly payouts:', error);
      }
      throw error;
    }
  },

  // Get monthly payout summary
  getMonthlyPayoutSummary: async (year, month) => {
    try {
      const response = await apiClient.get(
        `/api/v2/payouts/summary/${year}/${month}`
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching payout summary:', error);
      }
      throw error;
    }
  },

  // Get payslip data
  getPayslipData: async payoutId => {
    try {
      const response = await apiClient.get(`/api/payouts/${payoutId}/payslip`);
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching payslip data:', error);
      }
      throw error;
    }
  },

  // Download payslip as PDF
  downloadPayslip: async payoutId => {
    try {
      const response = await apiClient.get(`/api/payslip/pdf/${payoutId}`, {
        responseType: 'blob',
      });

      // Create blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      // Extract filename from Content-Disposition header
      const contentDisposition = response.headers['content-disposition'];
      let filename = `payslip_${payoutId}.pdf`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return { success: true, filename };
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error downloading payslip:', error);
      }
      throw error;
    }
  },

  // Get payslip history for an employee
  getPayslipHistory: async (employeeId, year) => {
    try {
      const response = await apiClient.get(
        `/api/v2/payslips/history/${employeeId}?year=${year}`
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching payslip history:', error);
      }
      throw error;
    }
  },

  // Email payslip to employee
  emailPayslip: async (payoutId, recipientEmail = null) => {
    try {
      const data = recipientEmail ? { recipient_email: recipientEmail } : {};
      const response = await apiClient.post(
        `/api/v2/payslips/email/${payoutId}`,
        data
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error emailing payslip:', error);
      }
      throw error;
    }
  },

  // Bulk generate payslips (Admin only)
  bulkGeneratePayslips: async (month, year, statusFilter = null) => {
    try {
      let url = `/api/v2/payslips/generate/bulk?month=${month}&year=${year}`;
      if (statusFilter) {
        url += `&status_filter=${statusFilter}`;
      }
      const response = await apiClient.post(url);
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error in bulk payslip generation:', error);
      }
      throw error;
    }
  },

  // Bulk email payslips (Admin only)
  bulkEmailPayslips: async (month, year) => {
    try {
      const response = await apiClient.post(
        `/api/v2/payslips/email/bulk?month=${month}&year=${year}`
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error in bulk payslip email:', error);
      }
      throw error;
    }
  },

  // Get employee payout history (using v2 endpoint)
  getEmployeePayoutHistory: async (employeeId, year) => {
    try {
      const response = await apiClient.get(
        `/api/v2/payouts/history/${employeeId}/${year}`
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching payout history:', error);
      }
      throw error;
    }
  },

  // Get my payout history (using v2 endpoint)
  getMyPayoutHistory: async year => {
    try {
      const response = await apiClient.get(`/api/v2/payouts/my-history/${year}`);
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error fetching my payout history:', error);
      }
      throw error;
    }
  },

  // Create payout schedule (using v2 endpoint)
  createPayoutSchedule: async schedule => {
    try {
      const response = await apiClient.post('/api/v2/payouts/schedule', schedule);
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error creating payout schedule:', error);
      }
      throw error;
    }
  },

  // Process scheduled payouts (manual trigger)
  processScheduledPayouts: async (targetDate = null) => {
    try {
      const data = targetDate ? targetDate : null;
      const response = await apiClient.post(
        '/api/v2/payouts/process-scheduled',
        data
      );
      return response.data;
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        // eslint-disable-next-line no-console
        console.error('Error processing scheduled payouts:', error);
      }
      throw error;
    }
  },

  // Utility functions
  formatCurrency: amount => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount || 0);
  },

  formatDate: dateString => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  },

  getStatusColor: status => {
    const statusColors = {
      pending: 'warning',
      processed: 'info',
      approved: 'success',
      paid: 'success',
      failed: 'error',
      cancelled: 'error',
    };
    return statusColors[status] || 'default';
  },

  getStatusLabel: status => {
    const statusLabels = {
      pending: 'Pending',
      processed: 'Processed',
      approved: 'Approved',
      paid: 'Paid',
      failed: 'Failed',
      cancelled: 'Cancelled',
    };
    return statusLabels[status] || status;
  },

  getMonthName: month => {
    const monthNames = [
      'January',
      'February',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ];
    return monthNames[month - 1] || '';
  },

  getCurrentFinancialYear: () => {
    const today = new Date();
    const currentYear = today.getFullYear();
    const currentMonth = today.getMonth() + 1; // getMonth() returns 0-11

    // Financial year in India runs from April 1 to March 31
    if (currentMonth >= 4) {
      return currentYear; // April to December of current year
    } else {
      return currentYear - 1; // January to March of next year
    }
  },

  getFinancialYearLabel: year => {
    return `FY ${year}-${(year + 1).toString().slice(-2)}`;
  },
};

export default payoutService;
