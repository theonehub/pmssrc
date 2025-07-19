import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api';

export const useReimbursementsQuery = (filters = {}) => {
  return useQuery({
    queryKey: ['reimbursements', filters],
    queryFn: async () => {
      const response = await apiClient.get('/v2/reimbursements/', { params: filters });
      return response.data;
    },
  });
}; 