import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api';

export const useOrganisationsQuery = (filters = {}) => {
  return useQuery({
    queryKey: ['organisations', filters],
    queryFn: async () => {
      const response = await apiClient.get('/api/v2/organisations/', { params: filters });
      return response.data;
    },
  });
}; 