import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api';

export const useTaxationQuery = (filters = {}) => {
  return useQuery({
    queryKey: ['taxation', filters],
    queryFn: async () => {
      const response = await apiClient.get('/api/v2/taxation/', { params: filters });
      return response.data;
    },
  });
}; 