import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api';

export const useLeavesQuery = (filters = {}) => {
  return useQuery({
    queryKey: ['leaves', filters],
    queryFn: async () => {
      const response = await apiClient.get('/api/v2/employee-leave/', { params: filters });
      return response.data;
    },
  });
}; 