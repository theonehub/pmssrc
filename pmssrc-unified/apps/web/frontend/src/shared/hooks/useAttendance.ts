import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api';

interface AttendanceFilters {
  employee_id?: string;
  month?: number;
  year?: number;
  date?: number;
}

export const useAttendanceQuery = (filters: AttendanceFilters = {}) => {
  return useQuery({
    queryKey: ['attendance', filters],
    queryFn: async () => {
      const { employee_id, month, year, date } = filters;
      
      // If we have employee_id, month, and year, use the specific endpoint
      if (employee_id && month && year) {
        const response = await apiClient.get(`/v2/attendance/employee/${employee_id}/month/${month}/year/${year}`);
        return response.data;
      }
      
      // If we have employee_id and year only, use year endpoint
      if (employee_id && year && !month) {
        const response = await apiClient.get(`/v2/attendance/employee/${employee_id}/year/${year}`);
        return response.data;
      }
      
      // If we have month and year but no employee_id, use "my" endpoints (current user)
      if (month && year && !employee_id) {
        const response = await apiClient.get(`/v2/attendance/my/month/${month}/year/${year}`);
        return response.data;
      }
      
      // If we have year only and no employee_id, use "my" year endpoint
      if (year && !month && !employee_id) {
        const response = await apiClient.get(`/v2/attendance/my/year/${year}`);
        return response.data;
      }
      
      // For team/manager views with date
      if (date && month && year && !employee_id) {
        const response = await apiClient.get(`/v2/attendance/team/date/${date}/month/${month}/year/${year}`);
        return response.data;
      }
      
      // For team/manager views with month
      if (month && year && !employee_id && !date) {
        const response = await apiClient.get(`/v2/attendance/team/month/${month}/year/${year}`);
        return response.data;
      }
      
      // Default fallback - get today's stats
      const response = await apiClient.get('/v2/attendance/stats/today');
      return response.data;
    },
    enabled: !!(filters.month || filters.year || Object.keys(filters).length === 0), // Enable if we have meaningful filters
  });
}; 