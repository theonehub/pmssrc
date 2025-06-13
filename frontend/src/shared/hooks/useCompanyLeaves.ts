import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api';

export const useCompanyLeavesQuery = (organisationId?: string) => {
  return useQuery({
    queryKey: ['companyLeaves', organisationId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/v2/company-leaves${organisationId ? `?organisation_id=${organisationId}` : ''}`);
      return response.data;
    },
  });
}; 