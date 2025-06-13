import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api';

export const useAttendanceQuery = (filters = {}) => {
  return useQuery({
    queryKey: ['attendance', filters],
    queryFn: async () => {
      const response = await apiClient.get('/api/v2/attendance/', { params: filters });
      return response.data;
    },
  });
}; 